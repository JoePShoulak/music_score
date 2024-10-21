from manim import *

# line thicknesses
THIN = 1.25
THICK = 3
STEM = 4

# TODO: Check if this makes the math simpler:
# https://music.stackexchange.com/questions/108517/i-dont-understand-the-bottom-number-in-a-time-signature

# region ERRORS
# TODO: consider adding more verbose output
class NotEnoughBeats(Exception):
	def __str__(self):
		return f"Not enough notes were provided to fill the measure."

# TODO: consider adding more verbose output
class TooManyBeats(Exception):
	def __str__(self):
		return f"Too many notes were provided to fill the measure."
	
# TODO: consider adding more verbose output
class InvalidNote(Exception):
	def __str__(self):
		return f"Invalid note provided"

# endregion
	
# region META
class NoteData:
	def __init__(self, duration, vMobj):
		self.duration = duration
		self.vMobj = vMobj

	def __add__(self, note):
		return self.duration + note.duration
	
	def __radd__(self, n):
		return self.duration + n
		
# endregion

class NoteHead(VMobject):
	def __init__(self, size, open=False, color=WHITE, **kwargs):
		super().__init__(**kwargs)
		head = Ellipse(1.618, 1, color=color).set_opacity(1)
		self.open = open

		if open:
			hole = Ellipse(1.618, 0.618, color=color, stroke_width=1).set_opacity(1)
			head = Cutout(head, hole, color=color, fill_opacity=1)
			
		self.become(head)
		self.rotate(21 * DEGREES).scale_to_fit_height(size)
		
	def set_color(self, color: ParsableManimColor, family: bool = True):
		if self.open:
			self[0].set_color(color, family)
		else:
			super().set_color(color, family)
		return self

class NoteStem(VMobject):
	def __init__(self, size, **kwargs):
		super().__init__(**kwargs)

		self.become(Line([0, 0, 0], [0, size*3, 0], stroke_width=STEM))

class Note(VMobject):
	def __init__(self, size, openHead=False, stem=True, color=WHITE, **kwargs):
		super().__init__(**kwargs)

		self.head = NoteHead(size, openHead, color=color)
		self.add(self.head)

		if stem:
			self.stem = NoteStem(size).align_to(self.head, DR).shift(UP*(2/3)*size)
			self.add(self.stem)

	def set_color(self, color: ParsableManimColor, family: bool = True):
		self.head.set_color(color, family)
		self.stem.set_color(color, family)

class QuarterNote(Note):
	def __init__(self, size=1, color=WHITE, **kwargs):
		super().__init__(size, color=color, **kwargs)

class HalfNote(Note):
	def __init__(self, size=1, color=WHITE, **kwargs):
		super().__init__(size, openHead=True, color=color, **kwargs)

class WholeNote(Note):
	def __init__(self, size=1, color=WHITE, **kwargs):
		super().__init__(size, openHead=True, stem=False, color=color, **kwargs)

class NoteTypes:
	WHOLE = NoteData(4, WholeNote)
	HALF = NoteData(2, HalfNote)
	QUARTER = NoteData(1, QuarterNote)

class Signature(VMobject):
	def __init__(self, size, signature=[4,4], **kwargs):
		super().__init__(**kwargs)
		self.become(MathTex(signature[0]).scale_to_fit_height(size))
		self.add(MathTex(signature[1]).scale_to_fit_height(size))
		self.arrange(DOWN, buff=0)

class Staff(VMobject):
	def __init__(self, time_signature=[4,4], **kwargs):
		super().__init__(**kwargs)
		width = max(time_signature[0], 2)*4/time_signature[1]
		
		self.noteLines = VGroup(
			*[Line([-width/2, 0, 0], [width/2, 0, 0], stroke_width=THIN) for i in range(5)]
		).arrange(DOWN)

		self.noteSize = self.noteLines[0].get_start()[1] - self.noteLines[1].get_start()[1]

		# bar lines
		self.barLines = VGroup(*[
			Line(self.noteLines[0].get_start(), self.noteLines[4].get_start(), stroke_width=THIN), 
			Line(self.noteLines[0].get_end(), self.noteLines[4].get_end(), stroke_width=THIN).shift(LEFT*0.125), 
			Line(self.noteLines[0].get_end(), self.noteLines[4].get_end(), stroke_width=THICK)
		])

		# time signature
		self.signature = Signature(2*self.noteSize, time_signature)
		self.signature.next_to(self.barLines[0], RIGHT, buff=0)

		self.add(self.noteLines, self.barLines, self.signature)
		self.noteBuff = (self.width - 1)/(4*time_signature[0]/time_signature[1] + 1)

class Measure(VMobject):
	def __init__(self, notes=[], signature=[4,4], **kwargs):
		super().__init__(**kwargs)
		self.staff = Staff(signature)

		noteMobs = []

		if len(notes):
			duration = 0
			k = 0
			beatFactor = signature[1]/4
			measureLength = signature[0]/beatFactor

			if notes[0].duration == measureLength: # If our note takes up the entire measure...
				if len(notes) > 1: raise TooManyBeats

				noteMobs = [notes[0].vMobj(self.staff.noteSize)] # all our notes are just this one
			else:
				for i, note in enumerate(notes):
					noteMob = note.vMobj(self.staff.noteSize) # create our note
					if i == 0:
						# if we're the first one, put it by the staff
						noteMob.next_to(self.staff.signature[0], RIGHT)
					else:
						# put it next to the last one, considering an offset k set by larger notes
						buff = self.staff.noteBuff + (self.staff.noteBuff + noteMob.width)*k
						noteMob.next_to(noteMobs[-1], RIGHT, buff=buff)

					# Align it to the center line and do some cleanup
					noteMob.align_to(self.staff.noteLines[3], DOWN).shift(UP*self.staff.noteSize/2)
					noteMobs += [noteMob]
					k = note.duration - 1
					duration += note.duration
					if duration > measureLength: raise TooManyBeats

				if duration < measureLength: raise NotEnoughBeats

		self.notes = VGroup(*noteMobs)
		self.add(self.staff, self.notes)
