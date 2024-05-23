#!/usr/bin/python3
# vim:set fileencoding=utf-8 et ts=4 sts=4 sw=4:
#
#   apt-listchanges - Show changelog entries between the installed versions
#                     of a set of packages and the versions contained in
#                     corresponding .deb files
#
#   Copyright (C) 2000-2006  Matt Zimmerman  <mdz@debian.org>
#   Copyright (C) 2006       Pierre Habouzit <madcoder@debian.org>
#   Copyright (C) 2016-2019  Robert Luberda  <robert@debian.org>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#

import sys, os, os.path
import functools
import apt_pkg
import signal
import subprocess
import traceback
from glob import glob

sys.path += [os.path.dirname(sys.argv[0]) + '/apt-listchanges', '/usr/share/apt-listchanges']
import ALCLog
from ALChacks import _
import apt_listchanges, DebianFiles, ALCApt, ALCConfig, ALCSeenDb

def main(config):
    apt_pkg.init()

    etc = apt_pkg.config.find_dir('Dir::Etc')
    conf = apt_pkg.config.find_file('Dir::Etc::apt-listchanges-main')
    if not conf: conf = os.path.join(etc, 'listchanges.conf')
    conf_d = apt_pkg.config.find_dir('Dir::Etc::apt-listchanges-parts')
    if conf_d == '/': conf_d = os.path.join(etc, 'listchanges.conf.d')

    configs = [conf]
    configs += glob(os.path.join(conf_d, '*.conf'))
    config.read(configs)
    debs = config.getopt(sys.argv)

    if config.dump_seen:
        ALCSeenDb.make_seen_db(config, True).dump()
        sys.exit(0)

    if config.apt_mode:
        debs = ALCApt.AptPipeline(config).read()
        if not debs:
            sys.exit(0)

    # Force quiet (loggable) mode if not running interactively
    if not sys.stdout.isatty() and not config.quiet:
        config.quiet = 1

    try:
        frontend = apt_listchanges.make_frontend(config, len(debs)+1)
    except apt_listchanges.EUnknownFrontend:
        ALCLog.error(_("Unknown frontend: %s") % config.frontend)
        sys.exit(1)

    if frontend is None:
        sys.exit(0)

    if frontend.needs_tty_stdin() and not sys.stdin.isatty():
        try:
            # Give any forked processes (eg. lynx) a normal stdin;
            # See Debian Bug #343423.  (Note: with $APT_HOOK_INFO_FD
            # support introduced in version 3.2, stdin should point to
            # a terminal already, so there should be no need to reopen it).
            with open('/dev/tty', 'rb+', buffering=0) as tty:
                os.close(0)
                os.dup2(tty.fileno(), 0)
        except Exception as ex:
            ALCLog.warning(_("Cannot reopen /dev/tty for stdin: %s") % str(ex))

    status = None
    if not config.show_all and config.since is None and config.latest is None:
        dpkg_status = apt_pkg.config.find_file('Dir::State::status')
        status = DebianFiles.ControlParser()
        status.readfile(dpkg_status)
        status.makeindex('Package')

    seen_db = ALCSeenDb.make_seen_db(config)

    # Mapping of source->binary packages
    source_packages = {}
    deb_number = 0
    for deb in debs:
        if deb_number % 8 == 0:
            frontend.update_progress()

        pkg = DebianFiles.Package(deb)
        source_packages.setdefault(pkg.source, []).append(pkg)
        deb_number += 1

    all_news = []
    all_changelogs = []
    all_binnmus = dict()
    notes = []

    # Main loop
    for srcpackage, binpackages in source_packages.items():
        (news, changelogs) = _process_srcpackage(config, seen_db, notes,
                                                 status, srcpackage,
                                                 binpackages)
        if news:
            all_news.append(news)
        if changelogs:
            all_changelogs.append(changelogs)
            if changelogs.binnmus:
                for binnmu in changelogs.binnmus:
                    all_binnmus.setdefault(binnmu.content, []).append(binnmu)


        bincount = len(binpackages)
        frontend.update_progress(bincount + int(deb_number/8) - int((deb_number+bincount)/8))
        deb_number += bincount


    frontend.progress_done()
    seen_db.close_db()

    for batch in (all_news, all_changelogs):
        batch.sort(key=lambda x: (x.numeric_urgency, x.package))
    for dummy, batch in all_binnmus.items():
        batch.sort(key=lambda x: (x.header))


    news    = _join_changes(all_news, source_packages,
                            config.headers, lambda package: _('News for %s') % package)
    changes = _join_changes(all_changelogs, source_packages,
                            config.headers, lambda package: _('Changes for %s') % package)
    binnmus = _join_binnmus(all_binnmus, config.headers)

    if binnmus:
        if changes:
            changes += '\n\n' + binnmus
        else:
            changes = binnmus

    if config.verbose and notes:
        joined_notes = _("Informational notes") + ":\n\n" + '\n'.join(notes)
        if config.which == "news":
            news += joined_notes
        else:
            changes += joined_notes

    if news or changes:
        _display(frontend, news,    lambda: _('apt-listchanges: News'))
        _display(frontend, changes, lambda: _('apt-listchanges: Changelogs'))

        apt_listchanges.confirm_or_exit(config, frontend)

        if apt_listchanges.can_send_emails(config):
            hostname = subprocess.getoutput('hostname')
            _send_email(news,    lambda: _("apt-listchanges: news for %s") % hostname)
            _send_email(changes, lambda: _("apt-listchanges: changelogs for %s") % hostname)

        # Write out seen db
        seen_db.apply_changes()

    elif not config.apt_mode and not source_packages.keys():
        ALCLog.error(_("Didn't find any valid .deb archives"))
        sys.exit(1)

def _determinefromversion(config, seen_db, notes, status, srcpackage, binpackages):
    if config.show_all:
        return None
    if srcpackage in seen_db:
        return seen_db[srcpackage]
    if config.since is not None:
        return config.since
    if config.latest is not None:
        return None

    result = None
    for pkg in binpackages:
        binpackage = pkg.binary
        statusentry = status.find('Package', binpackage)
        if not statusentry or not statusentry.installed():
            # Package not installed or seen
            notes.append(_("%s: will be newly installed") % binpackage)
        elif not result or apt_pkg.version_compare(result, statusentry.version()) < 0:
            result = statusentry.version()
    return result

def _drop_binnmu_suffix(version):
    pos = version.rfind('+')
    if pos != -1 and len(version) in range(pos+3, pos+7) and version[pos+1] == 'b':
        return version[:pos]
    return version


def _process_srcpackage(config, seen_db, notes, status, srcpackage, binpackages):
    fromversion = _determinefromversion(config, seen_db, notes, status, srcpackage, binpackages)
    if not fromversion and not config.show_all and config.latest is None:
        return (None, None)

    if len(binpackages) > 1:
        binpackages = sorted(binpackages,
                             key=functools.cmp_to_key(lambda x,y: apt_pkg.version_compare(y.Version, x.Version)))

    maxversion = binpackages[0].Version # XXX take the real version or we'll lose binNMUs
    processpkgs = []
    for pkg in binpackages:
        version = pkg.Version
        binpackage  = pkg.binary
        if fromversion and apt_pkg.version_compare(fromversion, version) >= 0:
            notes.append(_("%(pkg)s: Version %(version)s has already been seen")
                           % {'pkg': binpackage, 'version': version})
            break
        if version != maxversion and _drop_binnmu_suffix(version) != _drop_binnmu_suffix(maxversion):
            notes.append(_("%(pkg)s: Version %(version)s is lower than version of "
                           + "related packages (%(maxversion)s)")
                        % {'pkg': binpackage, 'version': version, 'maxversion' : maxversion})
            break
        processpkgs.append(pkg)

#    if config.debug and len(processpkgs) < len(binpackages):
#        ALCLog.debug("Ignored packages: %s" % ' '.join('%s=%s' % (x.binary, x.Version)
#                                                       for x in set(binpackages) - set(processpkgs)))

    if not processpkgs:
        return (None, None)

    (all_news, all_changelogs) = (None, None)
    for pkg in processpkgs:
        (news, changelog) = pkg.extract_changes(config.which, fromversion, config.latest, config.reverse)

        if news and not all_news:
            all_news = news
        if changelog and not all_changelogs:
            all_changelogs = changelog

        if all_changelogs or (all_news and config.which == "news"):
            break

    if not config.no_network and not all_changelogs and config.which != "news":
        for pkg in processpkgs:
            all_changelogs = pkg.extract_changes_via_apt(fromversion, config.latest, config.reverse)
            if all_changelogs:
                break

    if all_news or all_changelogs:
        seen_db[srcpackage] = maxversion

    return (all_news, all_changelogs)

def _join_changes(all_changes, source_packages, show_headers, header_package_getter):
    if not show_headers:
        return ''.join([x.changes for x in all_changes if x.changes])

    changes = ''
    for rec in all_changes:
        if rec.changes:
            package = rec.package
            header = header_package_getter(package)
            if next((x for x in source_packages[package] if x.binary != package), None):
                # Differing source and binary packages
                header  += ' (%s)'  % ' '.join(x.binary for x in source_packages[package])
            changes += '--- %s ---\n%s' % (header, rec.changes)
    return changes

def _join_binnmus(all_binnmus, show_headers):
    binnmus = ''
    for content, entries in all_binnmus.items():
        pkgs = '--- ' + _('Binary NMU of')
        sep = ': '
        lastlen = len(pkgs)
        for entry in entries:
            hdr = entry.header
            idx = hdr.find(')')
            if idx >= 0:
                hdr = hdr[:idx+1]

            # manually wrap the package lines
            pkgs += sep
            lastlen += len(sep)
            sep = ', '
            if lastlen + len(hdr) > 75:
                pkgs += '\n '
                lastlen = 1;
            pkgs += hdr
            lastlen += len(hdr)

        binnmus += pkgs + '\n\n' + content + '\n\n'

    return binnmus

def _display(frontend, changes, title_getter):
    if changes:
        frontend.set_title(title_getter())
        frontend.display_output(changes)

def _send_email(changes, subject_getter):
    if changes:
        apt_listchanges.mail_changes(config, changes, subject_getter())

def _setup_signals():
    def signal_handler(signum, frame):
        ALCLog.error(_('Received signal %d, exiting') % signum)
        sys.exit(apt_listchanges.BREAK_APT_EXIT_CODE)

    for s in [ signal.SIGHUP, signal.SIGQUIT, signal.SIGTERM ]:
        signal.signal(s, signal_handler)

if __name__ == '__main__':
    _setup_signals()
    config = ALCConfig.ALCConfig()
    try:
        main(config)
    except KeyboardInterrupt:
        sys.exit(apt_listchanges.BREAK_APT_EXIT_CODE)
    except ALCApt.AptPipelineError as ex:
        ALCLog.error(str(ex))
        sys.exit(apt_listchanges.BREAK_APT_EXIT_CODE)
    except ALCSeenDb.DbError as ex:
        ALCLog.error(str(ex))
        sys.exit(1)
    except Exception:
        traceback.print_exc()
        apt_listchanges.confirm_or_exit(config, apt_listchanges.ttyconfirm(config))
        sys.exit(1)
