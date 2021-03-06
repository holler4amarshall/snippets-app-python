import logging
import argparse
import psycopg2


# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")


def post(name, snippet, hide='false'):
    '''Store a snippet with an associated name.'''
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    cursor = connection.cursor()
    command = "insert into snippets values (%s, %s, %s)"
    cursor.execute(command, (name, snippet, hide))
    connection.commit()
    logging.debug("Snippet stored successfully.")
    return name, snippet
  

def get(name):
    '''Retrieve the snippet with a given name to return snippet. 
    If snippet not found, return 404 snippet not found error'''
    logging.info("Retrieving snippet {!r}".format(name))
    cursor = connection.cursor()
    command = "select message from snippets where keyword=%s and hidden='false'"
    cursor.execute(command, (name,))
    row = cursor.fetchone()
    if not row:
        # No snippet was found with that name.
        return "404: Snippet Not Found"
    return row[0]
    #return cursor.fetchone()
    #logging.error("FIXME: Unimplemented - get({!r})".format(name))
    #return ""
    
def catalogue():
    '''Get the list of public snippet names in order to search snippet by name'''
    logging.info("Retrieving list of public snippet name(s)")
    cursor = connection.cursor()
    command = "select keyword from snippets where hidden='false' order by keyword DESC"
    cursor.execute(command, ())
    results = cursor.fetchall()
    if not results:
        return "404: Snippet Not Found"
    keywords = ''
    for keyword in results: 
        keywords = keywords + keyword[0] + '; '
    return keywords[:-1]
        
def search(search_criteria):
    '''Return any snippets that contain the given search criteria in message'''
    logging.info("Retrieving snippets that contain '{!r}'".format(search_criteria))
    cursor = connection.cursor()
    search_criteria = '%' + search_criteria + '%'
    command = "select keyword, message from snippets where message like (%s)"
    cursor.execute(command, (search_criteria,))
    results = cursor.fetchall()
    statement = ''
    for keyword, message in results: 
        statement = statement + keyword + ': ' + message + '; '
    print(statement)
    if not results:
        return "404: Snippet Not Found"
    return statement[:-1]

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the post command
    logging.debug("Constructing post subparser")
    post_parser = subparsers.add_parser("post", help="Create a new snippet")
    post_parser.add_argument("name", help="Name of the snippet")
    post_parser.add_argument("snippet", help="Snippet text")
    post_parser.add_argument("-hi", "--hide", help="Optional argument to hide snippet from being searched by name", action="store_true")
    
    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    # Subparser for the catalogue command
    logging.debug("Constructing catalogue subparser")
    catalogue_parser = subparsers.add_parser("catalogue", help="Retrieve the list of names for snippets")
    # no arguments required
    
    # Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Search for a snippet that contains a given string")
    search_parser.add_argument("search_criteria", help="A string within the snippet text")


    args = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(args)
    command = arguments.pop("command")

    if command == "post":
        if args.hide:
            name, snippet = post(**arguments)
            print("Stored hidden key as {!r} as {!r}".format(snippet, name))
        else: 
            name, snippet = post(**arguments)
            print("Stored searchable key as {!r} as {!r}".format(snippet, name))
    if command == "catalogue":
        keywords = catalogue()
        print("Retrieving all snippet names: {!r}".format(keywords))
    if command == "search":
        params = arguments['search_criteria']
        search_query = search(**arguments)
        print("Retrieved all snippets that contain string: {!r}".format(params))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    

if __name__ == "__main__":
    main()