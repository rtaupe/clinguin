# Standard Python
from fastapi import FastAPI, APIRouter

import logging
import clingo

from pydantic import BaseModel
from typing import Sequence, Any

from importlib.metadata import metadata

# Self Defined
from clinguin.server.presentation.endpoints_helper import callFunction
from clinguin.server.presentation.backend_policy_dto import BackendPolicyDto

from clinguin.utils.logger import Logger


class Endpoints:
    def __init__(self, args) -> None:
        Logger.setupLogger(args.log_args)
        self._logger = logging.getLogger(args.log_args['name'])

        self.router = APIRouter()

        # Definition of endpoints
        self.router.add_api_route("/health", self.health, methods=["GET"])
        self.router.add_api_route("/", self.standardExecutor, methods=["GET"])
        self.router.add_api_route("/solver", self.policyExecutor, methods=["POST"])

        self._solver = []
        self._solver.append(args.solver(args))

    async def health(self):

        cuin = metadata('clinguin')
        return {
            "name": cuin["name"],
            "version": cuin["version"],
            "description": cuin["summary"]
        }

    async def standardExecutor(self):
        return self._solver[0].get()

    async def policyExecutor(self, solver_call_string: BackendPolicyDto):
        self._logger.debug("Got endpoint")
        symbol = clingo.parse_term(solver_call_string.function)
        function_name = symbol.name
        function_arguments = (
            list(map(lambda symb: str(symb), symbol.arguments)))

        self._logger.debug("Will call")
        result = callFunction(
            self._solver,
            function_name,
            function_arguments,
            {})
        return result
