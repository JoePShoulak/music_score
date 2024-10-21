from manim import *
from music_score import Measure, NoteTypes as NT

class Test(Scene):
    def construct(self):
        measure = Measure([NT.QUARTER, NT.HALF, NT.QUARTER])

        self.play(Write(measure))
        self.wait()
        