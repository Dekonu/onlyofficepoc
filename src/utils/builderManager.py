from copy import deepcopy
import json
import os
from urllib.parse import urlparse
import requests
from src.configuration import ConfigurationManager
from src.proxy import ProxyManager
from . import jwtManager, docManager, historyManager, fileUtils, serviceConverter

config_manager = ConfigurationManager()

def parseCommands(commands):
    """
    Will parse the list of commands and generate docbuilder code
    """
    return """
        var oParagraph = oDocument.GetElement(0);
        var oChart = Api.CreateChart("bar3D", [
        [200, 240, 280],
        [250, 260, 280]
        ], ["Projected Revenue", "Estimated Costs"], [2014, 2015, 2016], 4051300, 2347595, 24);
        var oFill = Api.CreateSolidFill(Api.CreateRGBColor(51, 51, 51));
        oChart.SetSeriesFill(oFill, 0, false);
        oFill = Api.CreateSolidFill(Api.CreateRGBColor(255, 111, 61));
        oChart.SetSeriesFill(oFill, 1, false);
        oChart.SetVerAxisTitle("USD In Hundred Thousands", 10);
        oChart.SetHorAxisTitle("Year", 11);
        oChart.SetLegendPos("bottom");
        oChart.SetShowDataLabels(false, false, true, false);
        oChart.SetTitle("Financial Overview", 13);
        oParagraph.AddDrawing(oChart);
        """
    docbuilderLines = []
    for command in commands:
        # do something, just going to add some random stuff for now
        docbuilderLines.append("something here")

def genDocbuilder(filename, fileExt, commands):
    """
    Builds a docbuilder file to send to the DocBuilder API
    """
    coreCommands = parseCommands(commands)
    
    docbuilder_content = f"""
    builder.CreateFile("{fileExt}");
    var oDocument = Api.GetDocument();
    {coreCommands}
    builder.SaveFile("{fileExt}","{filename}.{fileExt}");
    builder.CloseFile();
    """

    return docbuilder_content


# create a docbuilder request
def builderRequest(commands, req):
    headers={'accept': 'application/json'}

    filename = req.GET.get("fileName") or "new"
    fileExt = req.GET["fileExt"]

    returnEditor = req.GET.get("edit", True)
    storeHistory = req.GET.get("edithistory", True)

    # write some function to handle different commands but hardcode table for now
    payload = {}
    filename = docManager.getCorrectName(filename, req)
    print(filename)
    builderCode = genDocbuilder(filename, fileExt, commands)
    builder_file_path = docManager.getBuilderPath(filename, req)
    print(builder_file_path)
    with open(f"{builder_file_path}.docbuilder", "w+") as fh:
        fh.write(builderCode)

    payload["url"] = f"{config_manager.example_url().geturl()}/builder?fileName={filename}.docbuilder"
    payload["async"] = False

    if (jwtManager.isEnabled() and jwtManager.useForRequest()): # check if a secret key to generate token exists or not
        headerToken = jwtManager.encode({'payload': payload}) # encode a payload object into a header token
        headers[config_manager.jwt_header()] = f'Bearer {headerToken}' # add a header Authorization with a header token with Authorization prefix in it
        #payload doesn't need to contain token since it's in the header
        #payload['token'] = jwtManager.encode(payload) # encode a payload object into a body token

    response = requests.post(config_manager.document_builder_api_url().geturl(), json=payload, headers=headers, verify = config_manager.ssl_verify_peer_mode_enabled())
    response_body = response.json()

    try:
        if "urls" in response_body:
            doc_count = 0
            for doc in response_body["urls"].keys():
                doc_count+=1
                filename = docManager.getCorrectName(doc, req)
                filepath = docManager.getStoragePath(filename, req)
                # With save should probably be true
                docManager.downloadFileFromUri(response_body["urls"][doc], filepath, True)
                if storeHistory:
                    historyManager.createMeta(filepath, req)
            res = {}

            # in the case where the doc count is 0, it is likely that our code messed up
            if doc_count == 0:
                res = {
                    "status" : "error",
                    "message" : "no document was created, please check command notation",
                }
            elif doc_count != 1 or not returnEditor:
                res = {
                    "status" : "success",
                    "message" : "files successfully downloaded - no editor returned since more than one file was generated",
                    "files" : [response_body["urls"].keys()],
                    }
            else:
                # only looped once, last ref to filename is the filename we want
                res = {
                    "status" : "success",
                    "filename" : filename,
                }
    except Exception as e:
        res = {
            "status" : "error",
            "error" : str(e),
            }

    return res