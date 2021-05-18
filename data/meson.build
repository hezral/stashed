pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

desktop_file = i18n.merge_file(
  input: 'com.github.hezral.stashed.desktop.in',
  output: 'com.github.hezral.stashed.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.github.hezral.stashed.appdata.xml.in',
  output: 'com.github.hezral.stashed.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.github.hezral.stashed.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

install_data('application.css',
  install_dir: join_paths(pkgdatadir, 'stashed', 'data')
)

other_icon_sources = [
  join_paths('icons', 'com.github.hezral' + '-' + 'coffee' + '.svg'),
  join_paths('icons', 'com.github.hezral' + '-' + 'menu-symbolic' + '.svg'),
  join_paths('icons', 'com.github.hezral' + '-' + 'select' + '.svg'),
  join_paths('icons', 'com.github.hezral' + '-' + 'shortcuts' + '.svg'),
  join_paths('icons', 'system-search' + '.svg'),
]
iconsdir = join_paths(pkgdatadir, 'stashed', 'data', 'icons')
install_data(other_icon_sources, install_dir: iconsdir)