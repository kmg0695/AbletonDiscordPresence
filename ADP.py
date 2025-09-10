from _Framework.ControlSurface import ControlSurface
import Live
import threading
from time import time
from .drpc.discordrpc import RPC

FOLDER = '/AbletonDiscordPresence/'
SCRIPT_NAME = 'AbletonDiscordPresence'

class AbletonDiscordPresence(ControlSurface):
    __module__ = __name__
    __doc__ = "Ableton Discord Presence"

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.rpc = RPC(1414970197466681509)
        self.started_t = int(time())
        # self.show_message(SCRIPT_NAME)
        self.timer = None
        self.update_rpc()


    def disconnect(self):
        if self.timer: self.timer.cancel()
        ControlSurface.disconnect(self)

    def update_rpc(self):
        if self.timer: self.timer.cancel()
        def root_note(i):
            return ([
                "C",
                "C♯/D♭",
                "D",
                "D♯/E♭",
                "E",
                "F",
                "F♯/G♭",
                "G",
                "G♯/A♭",
                "A",
                "A♯/B♭",
                "B",
            ])[i]

        details = ""
        small_image = None
        small_image_text = None
        state = None
        with self.component_guard():
            # https://structure-void.com/PythonLiveAPI_documentation/Live11.0.xml
            live = Live.Application.get_application()
        song = live.get_document()
        state = f"{len(song.tracks)} tracks [{song.tempo} BPM, {root_note(song.root_note)} {song.scale_name}]"
        if song.is_playing:
            state = "Playing " + state
        if live.view.focused_document_view == "Session":
            # details = "[Sess]"
            small_image = "session-view"
            small_image_text = "In Session View"
        if live.view.focused_document_view == "Arranger":
            # details = "[Arr]"
            small_image = "arrangement-view"
            small_image_text = "In Arrangement View"

        t = song.view.selected_track
        c = song.view.detail_clip
        d = song.view.selected_parameter.canonical_parent if song.view.selected_parameter else None
        if c:
            if c.is_midi_clip:
                details += "Editing a MIDI clip"
            else:
                details += "Editing an audio clip"
        else:
            prefix = ""
            if t.has_midi_input:
                prefix = "On a "
                details += "MIDI Track"
            if t.has_audio_input:
                if t == song.master_track:
                    prefix = "On the "
                    details += "Master Track"
                else:
                    prefix = "On an "
                    details += "Audio Track"
            if d and hasattr(d, "name"):
                details += f" (tweaking {d.name})"
            else:
                details = prefix + details
            fx = len(t.devices)
            if fx > 0:
                details += f" w/ {fx} devices"
        

        self.rpc.set_activity(
            large_image="ableton-live",
            large_text=f"Live {live.get_major_version()}.{live.get_minor_version()}.{live.get_bugfix_version()}",
            small_image=small_image,
            small_text=small_image_text,
            details=details,
            state=state,
            ts_start=self.started_t
        )
        self.timer = threading.Timer(2, self.update_rpc)
        self.timer.start()

