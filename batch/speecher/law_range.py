class Keyword:
    part = "Part"
    chapter = "Chapter"
    section = "Section"


patent_civil_range = {
    Keyword.part: [
        {1: {}},
        {2: {}},
        {3: {}},
    ]
}


realtor_civil_range = {
    Keyword.part: [
        {1: {Keyword.chapter: [{5: {}}]}},
        {
            2: {
                Keyword.chapter: [
                    {1: {}},
                    {2: {}},
                    {3: {}},
                    {4: {}},
                    {5: {}},
                    {6: {}},
                    {7: {}},
                    {9: {}},
                ]
            }
        },
        {
            3: {
                Keyword.chapter: [
                    {
                        2: {
                            Keyword.section: [
                                {1: {}},
                                {3: {}},
                                {4: {}},
                                {7: {}},
                            ]
                        }
                    }
                ]
            }
        },
    ]
}

tax_civil_range = {
    Keyword.part: [
        {1: {}},
    ]
}

tax_commercial_range = {
    Keyword.part: [
        {3: {}},
    ]
}

labor_civil_range = {
    Keyword.part: [
        {1: {}, 3: {}},
    ]
}
