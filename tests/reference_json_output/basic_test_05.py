import json


class BasicTest05:
    @classmethod
    def get_reference_json(cls):
        json_dict = {"id":"root","type":"root","parent":"root","attributes":[],"do":[],"children":[{"id":"w","type":"window","parent":"root","attributes":[{"id":"w","key":"background_color","value":"pink"},{"id":"w","key":"child_layout","value":"grid"}],"do":[],"children":[{"id":"c3","type":"container","parent":"w","attributes":[{"id":"c3","key":"background_color","value":"\"#ffff00\""},{"id":"c3","key":"grid_column","value":"1"}],"do":[],"children":[{"id":"l33","type":"label","parent":"c3","attributes":[{"id":"l33","key":"label","value":"\"Label 3\""}],"do":[],"children":[]}]},{"id":"c2","type":"container","parent":"w","attributes":[{"id":"c2","key":"border_width","value":"3"},{"id":"c2","key":"background_color","value":"\"#707070\""},{"id":"c2","key":"grid_column","value":"0"}],"do":[],"children":[{"id":"c20","type":"container","parent":"c2","attributes":[{"id":"c20","key":"background_color","value":"\"#00ffff\""},{"id":"c20","key":"height","value":"20"}],"do":[],"children":[]},{"id":"l3","type":"label","parent":"c2","attributes":[{"id":"l3","key":"label","value":"\"This is another label\""}],"do":[],"children":[]},{"id":"l2","type":"label","parent":"c2","attributes":[{"id":"l2","key":"label","value":"\"This is a label\""}],"do":[],"children":[]}]}]}]}
        
        return json.loads(json.dumps(json_dict))
