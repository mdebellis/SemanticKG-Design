from franz.openrdf.model import URI
from src.ag_api import *
from franz.openrdf.repository.repositoryconnection import RepositoryConnection

print(hasattr(RepositoryConnection, 'shaclValidate'))

def run_shacl_validation(conn, shape_graph_uri_str, data_graph_uri=None, store_report=False, report_graph_uri=None):
    """
    Run SHACL validation in AllegroGraph.

    :param conn: An open AllegroGraph connection.
    :param shape_graph_uri_str: The URI (string) of the SHACL shape graph.
    :param data_graph_uri: Optional. The context URI (string) of the data to validate. If None, uses the default graph.
    :param store_report: If True, stores the validation report in the repository.
    :param report_graph_uri: If storing the report, this is the named graph to store it under.
    :return: A tuple (conforms: bool, report_text: str)
    """
    shape_graph = conn.createURI(shape_graph_uri_str)
    data_graph = conn.createURI(data_graph_uri) if data_graph_uri else None

    # Run SHACL validation
    result = conn.shaclValidate([data_graph], [shape_graph])

    conforms = result.getConforms()
    report_text = result.getMessage()

    print("SHACL conforms:", conforms)
    print(report_text)

    # Optionally store the report graph
    if store_report and report_graph_uri:
        report_graph = result.getReportGraph()
        report_context = conn.createURI(report_graph_uri)
        conn.addTriples(report_graph, contexts=[report_context])
        print(f"Validation report stored in graph: {report_graph_uri}")

    return conforms, report_text

#result = conn.shaclValidate([None], [conn.createURI("http://michaeldebellis.com/graph/shapes/people")])

