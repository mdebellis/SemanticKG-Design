from franz.openrdf.connect import ag_connect
from franz.openrdf.vocabulary import RDF
import os

stop_words1 = {'those', 'on', 'own', '’ve', 'yourselves', 'around', 'between', 'four', 'been', 'alone', 'off', 'am', 'then', 'other', 'can', 'regarding', 'hereafter', 'front', 'too', 'used', 'wherein', '‘ll', 'doing', 'everything', 'up', 'onto', 'never', 'either', 'how', 'before', 'anyway', 'since', 'through', 'amount', 'now', 'he', 'was', 'have', 'into', 'because', 'not', 'therefore', 'they', 'n’t', 'even', 'whom', 'it', 'see', 'somewhere', 'thereupon', 'nothing', 'whereas', 'much', 'whenever', 'seem', 'until', 'whereby', 'at', 'also', 'some', 'last', 'than', 'get', 'already', 'our', 'once', 'will', 'noone', "'m", 'that', 'what', 'thus', 'no', 'myself', 'out', 'next', 'whatever', 'although', 'though', 'which', 'would', 'therein', 'nor', 'somehow', 'whereupon', 'besides', 'whoever', 'ourselves', 'few', 'did', 'without', 'third', 'anything', 'twelve', 'against', 'while', 'twenty', 'if', 'however', 'herself', 'when', 'may', 'ours', 'six', 'done', 'seems', 'else', 'call', 'perhaps', 'had', 'nevertheless', 'where', 'otherwise', 'still', 'within', 'its', 'for', 'together', 'elsewhere', 'throughout', 'of', 'others', 'show', '’s', 'anywhere', 'anyhow', 'as', 'are', 'the', 'hence', 'something', 'hereby', 'nowhere', 'latterly', 'say', 'does', 'neither', 'his', 'go', 'forty', 'put', 'their', 'by', 'namely', 'could', 'five', 'unless', 'itself', 'is', 'nine', 'whereafter', 'down', 'bottom', 'thereby', 'such', 'both', 'she', 'become', 'whole', 'who', 'yourself', 'every', 'thru', 'except', 'very', 'several', 'among', 'being', 'be', 'mine', 'further', 'n‘t', 'here', 'during', 'why', 'with', 'just', "'s", 'becomes', '’ll', 'about', 'a', 'using', 'seeming', "'d", "'ll", "'re", 'due', 'wherever', 'beforehand', 'fifty', 'becoming', 'might', 'amongst', 'my', 'empty', 'thence', 'thereafter', 'almost', 'least', 'someone', 'often', 'from', 'keep', 'him', 'or', '‘m', 'top', 'her', 'nobody', 'sometime', 'across', '‘s', '’re', 'hundred', 'only', 'via', 'name', 'eight', 'three', 'back', 'to', 'all', 'became', 'move', 'me', 'we', 'formerly', 'so', 'i', 'whence', 'under', 'always', 'himself', 'in', 'herein', 'more', 'after', 'themselves', 'you', 'above', 'sixty', 'them', 'your', 'made', 'indeed', 'most', 'everywhere', 'fifteen', 'but', 'must', 'along', 'beside', 'hers', 'side', 'former', 'anyone', 'full', 'has', 'yours', 'whose', 'behind', 'please', 'ten', 'seemed', 'sometimes', 'should', 'over', 'take', 'each', 'same', 'rather', 'really', 'latter', 'and', 'ca', 'hereupon', 'part', 'per', 'eleven', 'ever', '‘re', 'enough', "n't", 'again', '‘d', 'us', 'yet', 'moreover', 'mostly', 'one', 'meanwhile', 'whither', 'there', 'toward', '’m', "'ve", '’d', 'give', 'do', 'an', 'quite', 'these', 'everyone', 'towards', 'this', 'cannot', 'afterwards', 'beyond', 'make', 'were', 'whether', 'well', 'another', 'below', 'first', 'upon', 'any', 'none', 'many', 'serious', 'various', 're', 'two', 'less', '‘ve'}
stop_words2 = {'goal','Target', 'Indicator', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.'}
all_stop_words = stop_words1.union(stop_words2)

AGRAPH_PASSWORD = os.getenv("AGRAPH_PASSWORD")
if not AGRAPH_PASSWORD:
    raise RuntimeError(
        "Environment variable AGRAPH_PASSWORD is not set. "
        "Please define it before running this script."
    )
conn = ag_connect('stream_forge_data_catalog', host='localhost', port=10035, user='mdebellis', password=AGRAPH_PASSWORD)

# Basic predicates for name (label) FTI
skos_alt_label_property = conn.createURI("http://www.w3.org/2004/02/skos/core#altLabel")
rdfs_label_property = conn.createURI("http://www.w3.org/2000/01/rdf-schema#label")
skos_pref_label_property = conn.createURI("http://www.w3.org/2004/02/skos/core#prefLabel")
basic_predicates_list = [skos_alt_label_property, skos_pref_label_property, rdfs_label_property]

# Predicates for content FTI
abstract_prop = conn.createURI("http://purl.org/dc/terms/abstract")
skos_definition_property_prop = conn.createURI("http://www.w3.org/2004/02/skos/core#definition")
skos_scope_note_prop = conn.createURI("http://www.w3.org/2004/02/skos/core#scopeNote")
docs_chunk_text_prop = conn.createURI("https://www.michaeldebellis.com/docs/chunk_text")
docs_chunk_title_prop = conn.createURI("https://www.michaeldebellis.com/docs/chunk_title")
first_name_prop = conn.createURI("https://www.michaeldebellis.com/dp/first_name")
last_name_prop = conn.createURI("https://www.michaeldebellis.com/dp/last_name")
intended_use_prop = conn.createURI("https://www.michaeldebellis.com/dp/intended_use")
lifecycle_stage_prop = conn.createURI("https://www.michaeldebellis.com/dp/lifecycle_stage")
comment_prop = conn.createURI("http://www.w3.org/2000/01/rdf-schema#comment")
content_predicate_list1 = [abstract_prop, skos_definition_property_prop, skos_scope_note_prop, docs_chunk_text_prop, docs_chunk_title_prop, first_name_prop, last_name_prop, intended_use_prop]
content_predicate_list2 = [lifecycle_stage_prop, comment_prop]
content_predicate_list = content_predicate_list1 + content_predicate_list2
all_fti_predicates_list = basic_predicates_list + content_predicate_list

conn.createFreeTextIndex("sf_name_search", predicates=basic_predicates_list, stopWords=all_stop_words, wordFilters=["stem.english"])
conn.createFreeTextIndex("sf_content_search", predicates=all_fti_predicates_list, stopWords=all_stop_words, wordFilters=["stem.english"])


