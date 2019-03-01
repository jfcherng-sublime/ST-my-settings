AutoSetIndentation has been updated. To see the changelog, visit
Preferences » Package Settings » AutoSetIndentation » Changelog


## 1.4.0

- Add back the `on_post_paste` event listener.
- Indentation could be re-detected again after a view goes blank.
- Remove setting: `enabled`. (Just disable this package from Package Control)
- Remove (maybe) useless event listeners:

  - on_activated_async
  - on_clone_async
  - on_modified_async
  - on_new_async
  - on_pre_save_async
