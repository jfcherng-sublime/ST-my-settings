from .IndentFinder.indent_finder import IndentFinder
import re
import sublime
import sublime_plugin


PLUGIN_NAME = __package__
PLUGIN_DIR = 'Packages/%s' % PLUGIN_NAME
PLUGIN_SETTINGS = '%s.sublime-settings' % PLUGIN_NAME


def plugin_message(message):
    return '[{0}] {1}'.format(PLUGIN_NAME, message)


def print_plugin_message(message, show_message=True):
    if show_message:
        print(plugin_message(message))


def show_status_message(message, show_message=True):
    settings = sublime.load_settings(PLUGIN_SETTINGS)

    if show_message and settings.get('show_status_message', True):
        sublime.status_message(message)


def is_view_at_front(view):
    return view.window() is not None and view.window().active_view() == view


def is_view_only_invisible_chars(view):
    return view.find(r'[^\s]', 0).begin() < 0


class AutoSetIndentationCommand(sublime_plugin.TextCommand):
    """ Examines the contents of the buffer to determine the indentation settings. """

    def run(self, edit, show_message=True, sample_length=2**16):
        """
        @brief Run the "auto_set_indentation" command.

        @param self         The object
        @param edit         The edit
        @param show_message The show message
        """

        settings = sublime.load_settings(PLUGIN_SETTINGS)

        sample = self.view.substr(sublime.Region(0, min(self.view.size(), sample_length)))
        indent_tab, indent_space = self.guess_indentation_from_string(sample)

        # unable to determine, use the default settings
        if indent_tab < 0 and indent_space < 0:
            self.use_indentation_default(settings.get('default_indentation'), show_message)
            return

        # more like mixed-indented
        if indent_tab > 0 and indent_space > 0:
            self.use_indentation_mixed(indent_tab, indent_space, show_message)
            return

        # tab-indented
        if indent_tab > 0:
            self.use_indentation_tab(indent_tab, show_message)
            return

        # space-indented
        if indent_space > 0:
            self.use_indentation_space(indent_space, show_message)
            return

    def guess_indentation_from_string(self, string):
        """
        @brief Guess the indentation of the given string.

        @param self   The object
        @param string The string

        @return (int, int) A tuple in the form of (indent_tab, indent_space)
                           (-1, -1) if unable to determine the indentation
        """

        result_unknown = ('unknown', -1)

        indent_finder = IndentFinder(result_unknown)
        indent_finder.parse_string(string)

        # possible outputs:
        #   - space X
        #   - tab Y
        #   - mixed tab Y space X
        #   - unknown -1 (the deault one from the constructor)
        result = str(indent_finder)

        # unable to determine the indentation
        if result == '%s %d' % result_unknown:
            return (-1, -1)

        indent_tab = re.search(r'\btab\s+([0-9]+)', result)
        indent_tab = int(indent_tab.group(1)) if indent_tab else 0

        indent_space = re.search(r'\bspace\s+([0-9]+)', result)
        indent_space = int(indent_space.group(1)) if indent_space else 0

        return (indent_tab, indent_space)

    def use_indentation_default(self, default_indentation, show_message=True):
        """
        @brief Sets the indentation to default.

        @param self                The object
        @param default_indentation The default indentation in the form of (indent_type, indent_size)
        @param show_message        The show message
        """

        indent_type, indent_size = default_indentation
        indent_type = indent_type.lower()

        if indent_type.startswith('tab'):
            self.use_indentation_tab(indent_size, False)

        if indent_type.startswith('space'):
            self.use_indentation_space(indent_size, False)

        show_status_message(
            plugin_message('Indentation: %s/%d (default)' % (indent_type, indent_size)),
            show_message
        )

    def use_indentation_mixed(self, indent_tab=4, indent_space=4, show_message=True):
        """
        @brief Sets the indentation to mixed.

        @param self         The object
        @param indent_tab   The indent tab size
        @param indent_space The indent space size
        @param show_message The show message
        """

        self.use_indentation_tab(indent_tab, False)

        show_status_message(
            plugin_message('Indentation: tab/%d space/%d (mixed)' % (indent_tab, indent_space)),
            show_message
        )

    def use_indentation_tab(self, indent_tab=4, show_message=True):
        """
        @brief Sets the indentation to tab.

        @param self         The object
        @param indent_tab   The indent tab size
        @param show_message The show message
        """

        self.view.settings().set('translate_tabs_to_spaces', False)
        self.view.settings().set('tab_size', indent_tab)

        show_status_message(
            plugin_message('Indentation: tab/%d' % indent_tab),
            show_message
        )

    def use_indentation_space(self, indent_space=4, show_message=True):
        """
        @brief Sets the indentation to space.

        @param self         The object
        @param indent_space The indent space size
        @param show_message The show message
        """

        self.view.settings().set('translate_tabs_to_spaces', True)
        self.view.settings().set('tab_size', indent_space)

        show_status_message(
            plugin_message('Indentation: space/%d' % indent_space),
            show_message
        )


class AutoSetIndentationEventListener(sublime_plugin.EventListener):
    def on_load_async(self, view):
        if self.is_event_listener_enabled('on_load_async'):
            self.set_indentation_for_view(view)

    def on_modified_async(self, view):
        # when the view is left only invisible chars (\s),
        # we assume the indentation of this view has not been detected yet
        if is_view_only_invisible_chars(view):
            view.settings().set('ASI_is_indentation_detected', False)

    def on_text_command(self, view, command_name, args):
        """
        @brief Replace Sublime Text's "detect_indentation" command with this plugin's.

        @param self         The object
        @param view         The view
        @param command_name The command name
        @param args         The arguments

        @return (str, dict) A tuple in the form of (command, arguments)
        """

        settings = sublime.load_settings(PLUGIN_SETTINGS)

        if (
            command_name != 'detect_indentation'
            or not settings.get('hijack_st_detect_indentation', True)
        ):
            return

        print_plugin_message('"%s" command hijacked' % command_name)

        return ('auto_set_indentation', {'show_message': is_view_at_front(view)})

    def on_post_text_command(self, view, command_name, args):
        """
        @brief Set the indentation when the user patses.

        @param self         The object
        @param view         The view
        @param command_name The command name
        @param args         The arguments
        """

        if (
            view.settings().get('ASI_is_indentation_detected', False)
            or not self.is_event_listener_enabled('on_post_paste')
            or (command_name != 'patse' and command_name != 'paste_and_indent')
        ):
            return

        self.set_indentation_for_view(view)

    def set_indentation_for_view(self, view, args={}):
        """
        @brief Set the indentation for the current view.

        @param self The object
        @param view The view
        """

        _args = {
            'show_message': is_view_at_front(view),
        }
        _args.update(args)

        view.run_command('auto_set_indentation', _args)
        view.settings().set('ASI_is_indentation_detected', True)

    def is_event_listener_enabled(self, event):
        """
        @brief Check if a event listener is enabled.

        @param self  The object
        @param event The event

        @return True if event listener enabled, False otherwise.
        """

        settings = sublime.load_settings(PLUGIN_SETTINGS)

        try:
            return settings.get('event_listeners', {})[event]
        except KeyError:
            print_plugin_message(
                '"event_listeners[%s]" is not set in user settings (assumed false)' %
                event
            )

            return False
