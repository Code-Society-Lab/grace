from discord.ext.commands import Cog, command, cooldown
from discord import Embed, File

import pymusicbox.symbolic.symbols as music_sym
from pymusicbox.synth.instrument import Instrument

import numpy
import scipy.io.wavfile as wavfile


class MusicCog(Cog, name="Music", description="Fun music-related commands."):
    def __init__(self, bot):
        self.bot = bot

    @command(name='melody', help='Hear a melody made of the notes you enter.')
    async def melody(self, ctx, *args):
        possible_notes = ['A', 'A#', 'B', 'C', 'C#',
                          'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

        file = None

        if not args:
            embed = Embed(
                color=self.bot.default_color,
                title=f"Melody",
                description="You need to enter some notes!"
            )

        elif not all([arg.upper() in possible_notes for arg in args]):
            embed = Embed(
                color=self.bot.default_color,
                title=f"Error",
                description="Your note inputs are invalid."
            )

        else:
            instrument = Instrument()

            notes = [music_sym.Note(pitch=arg, octave=3) for arg in args]
            track = music_sym.Track(list(range(len(args))), notes)

            wav_data = instrument.render_track(track).astype(numpy.int16)
            wavfile.write('output.wav', instrument.sample_rate, wav_data)

            file = File('output.wav')

            embed = Embed(
                color=self.bot.default_color,
                title=f"Melody",
                description="Your music here!"
            )

        await ctx.send(embed=embed, file=file)


def setup(bot):
    bot.add_cog(MusicCog(bot))