
def empty_to_none(x, option):
    """
    Fix empty list to None
    Click option with multiple=True returns a tuple.
    If option is not used, it returns an empty tuple when option is not called.
    However, in fordead, most of list are expected of type list
    and empty list should be None.

    This function tests if list is empty and removes option from dict x,
    i.e. setting the option value to None, otherwise it converts the tuple to a list updating x.

    Parameters
    ----------
    x : dict
        Click option with multiple=True
    option : str
        Option name

    Returns
    -------
    None
        The update of x is made by reference.
    """
    if len(x[option]) == 0:
        x.pop(option)
    else:
        # convert tuple to list
        x[option] = list(x[option])