import sublime
import sublime_plugin
import re


class decorateInlineCommentCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view

        # fmt: off
        cmtConfigs = [
            {
                'modifier': '//',
                'fill': '/',
                'fillWithPaddingSpaces': False,
                'reWhitespaces': None,
            },
            {
                'modifier': '#',
                'fill': '-',
                'fillWithPaddingSpaces': True,
                'reWhitespaces': None,
            },
        ]
        # fmt: on

        for cmtConfig in cmtConfigs:
            cmtConfig["reWhitespaces"] = re.compile(r"^(\s*)({})".format(cmtConfig["modifier"]))

        v.run_command("expand_selection", {"to": "scope"})

        for sel in v.sel():
            maxLength = 0
            lines = v.lines(sel)

            for lineRegion in lines:
                lineText = v.substr(lineRegion)

                cmtConfigMatched = None
                for cmtConfig in cmtConfigs:
                    matches = cmtConfig["reWhitespaces"].match(lineText)
                    if matches is not None:
                        cmtConfigMatched = cmtConfig
                        break

                if cmtConfigMatched is None:
                    raise Exception("No matched comment style...")

                leadingWS = matches.group(1)
                maxLength = max(maxLength, lineRegion.size())

            lineLength = maxLength - len(leadingWS + cmtConfigMatched["modifier"])

            # "expand selection to scope" may not select the trailing \n
            # in some syntaxes and we try to compensate it here
            lastCharInScope = v.substr(sublime.Region(sel.end() - 1, sel.end()))
            if lastCharInScope != "\n":
                leadingEol = "\n"
                endingEol = ""
            else:
                leadingEol = ""
                endingEol = "\n"

            if cmtConfigMatched["fillWithPaddingSpaces"]:
                midContentForBeginEndLines = " " + cmtConfigMatched["fill"] * (lineLength - 1) + " "
            else:
                midContentForBeginEndLines = cmtConfigMatched["fill"] * (lineLength + 1)

            # insert ending line
            v.insert(
                edit,
                sel.end(),
                (
                    leadingEol
                    + leadingWS
                    + cmtConfigMatched["modifier"]
                    + midContentForBeginEndLines
                    + cmtConfigMatched["modifier"]
                    + endingEol
                ),
            )

            for lineRegion in reversed(lines):
                line = v.substr(lineRegion)

                # 1 for at least 1 extra trailing whitespace
                rPadding = 1 + (maxLength - lineRegion.size())

                prefix = leadingWS + cmtConfigMatched["modifier"]
                postfix = (" " * rPadding) + cmtConfigMatched["modifier"]
                cmtContent = line[len(leadingWS + cmtConfigMatched["modifier"]) :]

                v.replace(edit, lineRegion, prefix + cmtContent + postfix)

            # insert begin line
            v.insert(
                edit,
                sel.begin(),
                (
                    cmtConfigMatched["modifier"]
                    + midContentForBeginEndLines
                    + cmtConfigMatched["modifier"]
                    + "\n"
                    + leadingWS
                ),
            )
