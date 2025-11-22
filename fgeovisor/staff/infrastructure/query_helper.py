
def is_query_valid(query_dict, q_equals, n) -> bool:
    """ Use it when you need to restrict URL parameters. """
    query_len = len(query_dict.keys())

    if query_len != n:
        return False
    
    if q_equals != set():
        return False

    return True