from typing import Optional
from grace.model import Model, Field


class Thank(Model):
    """A class representing a Thank record in the database."""

    __tablename__ = "thanks"

    id: int | None = Field(default=None, primary_key=True)
    member_id: int = Field(unique=True)
    count: int = Field(default=0)

    @property
    def rank(self) -> Optional[str]:
        """Returns the rank of the member based on the number of times they
        have been thanked.

        :return: The rank of the member.
        :rtype: Optional[str]
        """
        if self.count in range(1, 11):
            return "Intern"
        elif self.count in range(11, 21):
            return "Helper"
        elif self.count in range(21, 31):
            return "Vetted helper"
        elif self.count > 30:
            return "Expert"
        else:
            return None
