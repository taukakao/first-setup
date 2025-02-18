install_data(
    'firstsetup-session.desktop',
    rename: 'firstsetup.desktop',
    install_dir: join_paths(get_option('datadir'), 'xsessions')
)

install_data(
    'firstsetup-session.desktop',
    rename: 'firstsetup.desktop',
    install_dir: join_paths(get_option('datadir'), 'wayland-sessions')
)

install_data(
    'firstsetup-session.desktop',
    rename: 'firstsetup.desktop',
    install_dir: join_paths(get_option('datadir'), 'gnome-session', 'sessions')
)

install_data(
    'firstsetup-session-mode.json',
    rename: 'firstsetup.json',
    install_dir: join_paths(get_option('datadir'), 'gnome-shell', 'modes')
)

install_data(
    'org.vanillaos.FirstSetup.policy',
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'polkit-1', 'actions')
)

install_data(
    'org.vanillaos.FirstSetup.rules',
    install_dir: join_paths(get_option('prefix'), get_option('datadir'), 'polkit-1', 'rules.d')
)

desktop_file = i18n.merge_file(
  input: 'org.vanillaos.FirstSetup.desktop.in',
  output: 'org.vanillaos.FirstSetup.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications'),
)

custom_target(
  'install-autostart-desktop',
  input: desktop_file,
  output: 'org.vanillaos.FirstSetup.autostart.desktop',
  command: ['cp', '@INPUT@', '@OUTPUT@'],
  install_dir: join_paths(get_option('sysconfdir'), 'skel', '.config', 'autostart'),
  build_by_default: true,
  install : true,
)

custom_target(
  'validate-desktop-file',
  command: ['desktop-file-validate', '@INPUT@'],
  input: desktop_file,
  output: 'desktop-file-validation',
  build_by_default: true,
)

subdir('icons')
