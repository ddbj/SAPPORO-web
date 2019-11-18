# coding: utf-8
from collections import OrderedDict
from urllib import parse

import yaml

yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                     lambda loader,
                     node: OrderedDict(loader.construct_pairs(node)))


def parse_cwl_input_params(cwl_file):
    """
    inputs: cwl_file -> str
    outputs: input_params -> list
        {
            label: str
            type: str (boolean, int, float, string)
                - int, long, double -> int
                - string, File, Directoru -> string
            default: str, boolean, int, float, None
            doc: str or None
        }
    """
    d_cwl_file = yaml.load(cwl_file, Loader=yaml.SafeLoader)  # NOQA TODO fix yaml or json
    assert "inputs" in d_cwl_file, "CWL file does not have inputs field."
    input_params = []
    for label, d_values in d_cwl_file["inputs"].items():
        assert "type" in d_values, "The content of CWL file is incorrect"
        input_param = dict()
        input_param["label"] = label
        input_param["type"] = d_values["type"].strip("?")
        if "default" in d_values:
            input_param["default"] = d_values["default"]
        else:
            input_param["default"] = None
        if "doc" in d_values:
            input_param["doc"] = d_values["doc"]
        else:
            if "label" in d_values:
                input_param["doc"] = d_values["label"]
            else:
                input_param["doc"] = None
        input_params.append(input_param)

    return input_params


def change_cwl_url_to_cwl_viewer_url(input_url):
    """
    a = "https://raw.githubusercontent.com/suecharo/SAPPORO/master/SAPPORO-service/test/test_workflow/trimming_and_qc.cwl"  # NOQA
    b = "https://github.com/suecharo/SAPPORO/blob/master/SAPPORO-service/test/test_workflow/trimming_and_qc.cwl"  # NOQA
    c = "https://view.commonwl.org/workflows/github.com/suecharo/SAPPORO/blob/master/SAPPORO-service/test/test_workflow/trimming_and_qc.cwl"  # NOQA
    assert change_cwl_url_to_cwl_viewer_url(a) == c
    assert change_cwl_url_to_cwl_viewer_url(b) == c
    """

    input_url_parsed = parse.urlparse(input_url)
    if input_url_parsed.netloc == "raw.githubusercontent.com":
        new_path = "/workflows/github.com" + input_url_parsed.path
        l_new_path = new_path.split("/")
        l_new_path.insert(5, "blob")
        new_path = "/".join(l_new_path)
        viewer_url_parsed = input_url_parsed._replace(scheme="https", netloc="view.commonwl.org", path=new_path)  # NOQA
        viewer_url = parse.urlunparse(viewer_url_parsed)
    elif input_url_parsed.netloc == "github.com":
        viewer_url_parsed = input_url_parsed._replace(scheme="https", netloc="view.commonwl.org", path="/workflows/github.com" + input_url_parsed.path)  # NOQA
        viewer_url = parse.urlunparse(viewer_url_parsed)
    else:
        return False

    return viewer_url
