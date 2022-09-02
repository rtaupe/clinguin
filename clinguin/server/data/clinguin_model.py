"""
Module that contains the ClinguinModel class.
"""
import logging
import clorm

from clorm import Raw
from clingo import Control,parse_term
from clingo.symbol import Function, Number, String

from clinguin.utils import NoModelError, Logger

from .element import ElementDao
from .attribute import AttributeDao
from .callback import CallbackDao

class ClinguinModel:
    """
    The ClinguinModel is the low-level-access-class for handling clorm and clingo, regarding brave-cautious and other default things. This class provides functionality to create a factbase with brave-cautious extended files, functionality to query important things for clinguin, etc.
    """

    def __init__(self, factbase=None):
        self._logger = logging.getLogger(Logger.server_logger_name)

        self.unifiers = [ElementDao, AttributeDao, CallbackDao]

        if factbase is None:
            self._factbase = clorm.FactBase([])
        else:
            self._factbase = factbase

    def __str__(self):
        return self._factbase.asp_str()

    @classmethod
    def fromWidgetsFile(cls, ctl, widgets_files, assumptions):
        """
        Creates a ClinguinModel from paths of widget files and assumptions.
        """
        prg = cls.getCautiousBrave(ctl,assumptions)
        return cls.fromWidgetsFileAndProgram(ctl,widgets_files,prg)

    @classmethod
    def fromWidgetsFileAndProgram(cls, ctl, widgets_files, prg):
        """
        Creates a ClinguinModel from a Clingo control object, paths of the widget-files and a logic program provided as a string (prg is a string which contains a logic program)
        """

        model = cls()

        wctl = cls.widControl(widgets_files, prg)

        with wctl.solve(yield_=True) as result:
            for m in result:
                model_symbols = m.symbols(shown=True)
                break

        model._setFbSymbols(model_symbols)
        return model

    @classmethod
    def widControl(cls, widgets_files, extra_prg=""):
        """
        Generates a ClingoControl Object from paths of widget files and extra parts of a logic program given by a string.
        """
        wctl = Control(['0','--warn=none'])
        for f in widgets_files:
            try:
                wctl.load(str(f))
            except Exception as e:
                logger = logging.getLogger(Logger.server_logger_name)
                logger.critical("File %s  could not be loaded - likely not existant or syntax error in file!", str(f))
                raise e
        
        wctl.add("base",[],extra_prg)
        wctl.add("base",[],"#show element/3. #show attribute/3. #show callback/3.")
        wctl.ground([("base",[])])

        return wctl


    @classmethod
    def fromBCExtendedFile(cls, ctl,assumptions):
        """
        Creates a ClinguinModel instance from a ClingoControl object and the provided assumptions.
        """

        logger = logging.getLogger(Logger.server_logger_name)

        ctl.assign_external(parse_term('show_all'),False)
        ctl.assign_external(parse_term('show_cautious'),False)
        ctl.assign_external(parse_term('show_untagged'),False)
        ctl.assign_external(parse_term('show_brave'),True)
        brave_model = cls.fromBraveModel(ctl,assumptions, logger)
        # Here we could see if the user wants none tagged as cautious by default
        ctl.assign_external(parse_term('show_brave'),False)
        ctl.assign_external(parse_term('show_untagged'),True)
        cautious_model = cls.fromCautiousModel(ctl,assumptions, logger)
        ctl.assign_external(parse_term('show_untagged'),False)
        ctl.assign_external(parse_term('show_all'),True)

        return cls.combine(brave_model,cautious_model, logger)
    

    @classmethod
    def combine(cls, cgmodel1, cgmodel2):
        """
        Combines the factbases of two ClinguinModels to one factbase, i.e. two ClinguinModels become one per Union.
        """
        return cls(cgmodel1._factbase.union(cgmodel2._factbase))

    @classmethod
    def fromClingoModel(cls, m):
        """ 
        Creates a ClinguinModel from a clingo model.
        """
        model = cls()
        model._setFbSymbols(m.symbols(shown=True))
        return model

    @classmethod
    def fromBraveModel(cls, ctl, assumptions):
        model = cls()
        brave_model = model.computeBrave(ctl, assumptions)
        model._setFbSymbols(brave_model)
        return model

    @classmethod
    def fromCautiousModel(cls, ctl, assumptions):
        model = cls()
        cautious_model = model.computeCautious(ctl, assumptions)
        model._setFbSymbols(cautious_model)
        return model

    @classmethod
    def getCautiousBrave(cls, ctl, assumptions):
        model = cls()

        cautious_model = model.computeCautious(ctl, assumptions)
        brave_model = model.computeBrave(ctl, assumptions)
        # c_prg = self.tagCautiousPrg(cautious_model)
        c_prg = model.symbolsToPrg(cautious_model)
        b_prg = model.tagBravePrg(brave_model)
        return c_prg+b_prg

    @classmethod
    def fromCtl(cls, ctl):
        model = cls()
        with ctl.solve(yield_=True) as result:
            for m in result:
                model_symbols = m.symbols(shown=True)
                break

        model._setFbSymbols(model_symbols)
        return model


    def addMessage(self,title,message):
        """
        Adds a ''Message'' (aka. Notification/Pop-Up) for the user with a certain title and message.
        """
        self.addElement("message","message","window")
        self.addAttribute("message","title",title)
        self.addAttribute("message","message",message)

    def tag(self, model, tag):
        tagged = []
        for s in model:
            tagged.append(Function(tag,[s]))
        return tagged

    def symbolsToPrg(self,symbols):
        return "\n".join([str(s)+"." for s in symbols])

    def tagBravePrg(self, model):
        tagged = self.tag(model,'_b')
        return self.symbolsToPrg(tagged)
    
    def tagCautiousPrg(self, model):
        tagged = self.tag(model,'_c')
        return self.symbolsToPrg(tagged)


    def addElement(self, id, t, parent):
        if type(id)==str:
            id = Function(id,[])
        if type(t)==str:
            t = Function(t,[])
        if type(parent)==str:
            parent = Function(parent,[])
        self._factbase.add(ElementDao(Raw(id),Raw(t),Raw(parent)))

    def addAttribute(self, id, key, value):
        if type(id)==str:
            id = Function(id,[])
        if type(key)==str:
            key = Function(key,[])
        if type(value)==str:
            value = String(value)
        if type(value)==int:
            value = Number(value)
        self._factbase.add(AttributeDao(Raw(id),Raw(key),Raw(value)))

    def filterElements(self, condition):
        elements = self.getElements()
        kept_elements = [e for e in elements if condition(e)]
        kept_ids = [e.id for e in kept_elements]
        attributes = self.getAttributes()
        callbacks = self.getCallbacks()
        kept_attributes = [e for e in attributes if e.id in kept_ids]
        kept_callbacks = [e for e in callbacks if e.id in kept_ids]
        self._factbase=clorm.FactBase(kept_elements+kept_callbacks+kept_attributes)

    def getElements(self):
        return self._factbase.query(ElementDao).all()
    
    def getAttributes(self):
        return self._factbase.query(AttributeDao).all()

    def getAttributesGrouped(self):
        return self._factbase.query(AttributeDao).group_by(AttributeDao.id).all()

    def getCallbacksGrouped(self):
        return self._factbase.query(CallbackDao).group_by(CallbackDao.id).all()

    def getCallbacks(self):
        return self._factbase.query(CallbackDao).all()

    def getAttributesForElementId(self, element_id):
        return self._factbase.query(AttributeDao).where(
            AttributeDao.id == element_id).all()

    def getCallbacksForElementId(self, element_id):
        return self._factbase.query(CallbackDao).where(
            CallbackDao.id == element_id).all()
    
    def _setFbSymbols(self, symbols):
        self._factbase = clorm.unify(self.unifiers, symbols)

    def _compute(self,ctl, assumptions):
        with ctl.solve(assumptions=[(a,True) for a in assumptions],
                yield_=True) as result:
            model_symbols = None
            for m in result:
                model_symbols = m.symbols(shown=True,atoms=False)
        if model_symbols is None:
            raise NoModelError
        return list(model_symbols)

    def computeBrave(self, ctl, assumptions):
        ctl.configuration.solve.enum_mode = 'brave'
        return self._compute(ctl, assumptions)
    
    def computeCautious(self, ctl, assumptions):
        ctl.configuration.solve.enum_mode = 'cautious'
        return self._compute(ctl, assumptions)

    def computeAuto(self, ctl, assumptions):
        ctl.configuration.solve.enum_mode = 'auto'
        return self._compute(ctl, assumptions)


    def getFactbase(self):
        return self._factbase

