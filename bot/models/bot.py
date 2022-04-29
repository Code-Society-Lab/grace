from sqlalchemy import String, Column, Integer, BigInteger
from sqlalchemy.orm import relationship
from bot import app
from bot.models.bot_channel import BotChannel
from db.model import Model


class Bot(app.base, Model):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    prefix = Column(String(255), nullable=False)
    description = Column(String(255))
    default_color_code = Column(String(255))

    welcome_message = Column(String(255))
    channels = relationship("BotChannel", cascade="all")

    @classmethod
    def get_current(cls):
        return cls.first()

    def get_channel(self, **kwargs):
        """Returns the corresponding channel informations

        :param **kwargs
            Possible argument:
                name : The channel name
                id : The channel id

        :return channel (
            Will return 'NoneM if the the channel is not found

        :raise ValueError
            If the parameter are not valid, a 'ValueError' exception will be raised.

        Ex.
            ```
                # Retrieve the channel with the name of the channel
                get_channel(name="channel-name")

                # Retrieve the channel with the id of the channel
                get_channel(id="827698582861512714")
            ```
        """
        channel_name = kwargs.get("name", None)
        channel_id = kwargs.get("id", None)

        if channel_name:
            channel = BotChannel.where(bot_id=self.id, channel_name=channel_name)
        elif channel_id:
            channel = BotChannel.where(bot_id=self.id, channel_id=channel_id)
        else:
            raise ValueError("You need to pass the channel 'id' or channel 'name'")

        if channel:
            return channel.first()

        return None
