from typing import Optional, List
from sqlalchemy import desc, Column, Integer, BigInteger
from grace.model import Model
from bot import app


class Thank(app.base, Model):
    """A class representing a Thank record in the database."""

    __tablename__ = 'thanks'

    id = Column(Integer, primary_key=True)
    member_id = Column(BigInteger, nullable=False, unique=True)
    count = Column(Integer, default=0)

    @property
    def rank(self) -> Optional[str]:
        """Returns the rank of the member based on the number of times they
        have been thanked.

        :return: The rank of the member.
        :rtype: Optional[str]
        """
        if self.count in range(1, 11):
            return 'Intern'
        elif self.count in range(11, 21):
            return 'Helper'
        elif self.count in range(21, 31):
            return 'Vetted helper'
        elif self.count > 30:
            return 'Expert'
        else:
            return None

    @classmethod
    def ordered(cls) -> List['Thank']:
        """Returns a list of all `Thank` objects in the database, ordered by
        the `count` attribute in descending order.

        :return: A list of `Thank` objects.
        :rtype: List[Thank]
        """
        return cls.query().order_by(desc(cls.count)).all()
