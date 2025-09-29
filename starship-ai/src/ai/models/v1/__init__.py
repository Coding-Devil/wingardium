#  Copyright (c) 2025 Nokia - Nokia Proprietary Internal Use Only - All Rights Reserved.

# The following apply to each model.

# The pattern foo: Optional[bar] = Field(...) means that field foo is required but may
# have None as a value as well as something of type bar.  The pattern foo: bar = Field(...)
# means that field foo is required and must have a value of type bar (which may or may not
# include None).  The latter is the same as just doing foo: bar.
# See https://pydantic-docs.helpmanual.io/usage/models/#required-fields

# Constrained strings with a regex are listed separately.  This is to make flake8 happy
# (and to make them potentially reusable).  Putting them inline will cause errors in flake8
# due to the way it does forward refs vs the way pydantic does (flake8 follows the PEP,
# pydantic doesn't - at least currently)

__model_version__ = 'v1'
