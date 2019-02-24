import re
import sublime
import sublime_plugin
from .IndentFinder.indent_finder import IndentFinder


def show_status_message(message, show_message=True):
    if show_message:
        sublime.status_message(message)


class DetectIndentationCommand(sublime_plugin.TextCommand):
    """Examines the contents of the buffer to determine the indentation settings."""

    def run(self, edit, show_message=True, threshold=10, sample_length=2**16):
        """
        @brief Run the command.

        @param self         The object
        @param edit         The edit
        @param show_message The show message
        """

        sample = self.view.substr(sublime.Region(0, min(self.view.size(), sample_length)))
        indent_tab, indent_space = self.guess_indentation_from_string(sample)

        # more like mixed-indented
        if indent_tab > 0 and indent_space > 0:
            self.set_mixed_indentation(indent_tab, indent_space)
            return

        # tab-indented
        if indent_tab > 0:
            self.set_tab_indentation(indent_tab)
            return

        # space-indented
        if indent_space > 0:
            self.set_space_indentation(indent_space)
            return

    def guess_indentation_from_string(self, string):
        """
        @brief Guess the indentation of the given string.

        @param self   The object
        @param string The string

        @return (int, int) A tuple in the form of (indent_tab, indent_space)
        """

        indent_finder = IndentFinder()
        indent_finder.parse_string(string)

        # possible outputs:
        #   - space X
        #   - tab Y
        #   - mixed tab Y space X
        result = str(indent_finder)

        indent_tab = re.search(r'\btab\s+([0-9]+)', result)
        indent_tab = int(indent_tab.group(1)) if indent_tab else 0

        indent_space = re.search(r'\bspace\s+([0-9]+)', result)
        indent_space = int(indent_space.group(1)) if indent_space else 0

        return (indent_tab, indent_space)

    def set_mixed_indentation(self, indent_tab=4, indent_space=4, show_message=True):
        self.set_tab_indentation(indent_tab, False)
        show_status_message(
            str('Indentation: tab/%d space/%d (mixed)' % (indent_tab, indent_space)),
            show_message
        )

    def set_tab_indentation(self, indent_tab=4, show_message=True):
        self.view.settings().set('translate_tabs_to_spaces', False)
        self.view.settings().set('tab_size', indent_tab)
        show_status_message(
            str('Indentation: tab/%d' % indent_tab),
            show_message
        )

    def set_space_indentation(self, indent_space=4, show_message=True):
        self.view.settings().set('translate_tabs_to_spaces', True)
        self.view.settings().set('tab_size', indent_space)
        show_status_message(
            str('Indentation: space/%d' % indent_space),
            show_message
        )


class DetectIndentationEventListener(sublime_plugin.EventListener):
    # I modified this load event to be "async"
    def on_load_async(self, view):
        if view.settings().get('detect_indentation'):
            is_at_front = (view.window() is not None and view.window().active_view() == view)
            view.run_command('detect_indentation', {'show_message': is_at_front})
