

def get_username(firstname, lastname):
    if firstname and lastname:
        return u"{}{}".format(firstname[0], lastname)

    return u"{}{}".format(firstname, lastname)
