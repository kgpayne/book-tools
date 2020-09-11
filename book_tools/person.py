import probablepeople


class NameParseError(Exception):
    pass


class Name:

    def __init__(
        self, given_name=None, surname=None, middle_name=None,
        first_initial=None, last_initial=None, middle_initial=None,
        prefix_marital=None, prefix_other=None,
        suffix_generational=None, suffix_other=None,
        nickname=None
    ):
        assert given_name or first_initial, "A valid name must have either a 'given_name' or 'first_initial' specified."

        self.given_name = given_name
        self.surname = surname
        self.middle_name = middle_name or []

        self.first_initial = first_initial
        self.last_initial = last_initial
        self.middle_initial = last_initial or []

        self.prefix_marital = prefix_marital
        self.prefix_other = prefix_other
        self.suffix_generational = suffix_generational
        self.suffix_other = suffix_other
        self.nickname = nickname

    def __repr__(self):
        return (
            "Name('"
            f"{self.given_name if self.given_name else self.first_initial} "
            f"{self.surname if self.surname else self.last_initial}"
            "')"
        )

    def __str__(self):
        return (
            f"{self.given_name if self.given_name else self.first_initial} "
            f"{self.surname if self.surname else self.last_initial}"
        )

    @classmethod
    def from_string(cls, text):
        try:
            tagged_name, name_type = probablepeople.tag(text)
        except probablepeople.RepeatedLabelError as e:
            raise NameParseError(
                "Could not parse name (RepeatedLabelError). "
                "it is likely that either: \n"
                "(1) the input string is not a valid person/corporation name, or\n"
                "(2) some tokens were labeled incorrectly."
            ) from e
        if name_type == 'Person':
            return cls(
                given_name=tagged_name.get('GivenName'),
                first_initial=tagged_name.get('FirstInitial'),

                surname=tagged_name.get('Surname'),
                last_initial=tagged_name.get('LastInitial'),

                middle_name=tagged_name.get('MiddleName'),
                middle_initial=tagged_name.get('MiddleInitial'),

                prefix_marital=tagged_name.get('PrefixMarital'),
                prefix_other=tagged_name.get('PrefixOther'),

                suffix_other=tagged_name.get('SuffixOther'),
                suffix_generational=tagged_name.get('SuffixGenerational')
            )
