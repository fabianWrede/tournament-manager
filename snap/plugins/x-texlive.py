import os
from subprocess import Popen, PIPE

# pylint: disable=E0401
import snapcraft
from snapcraft.plugins import dump

extras = ["koma-script", "lm", "microtype", "booktabs", "ltablex"]

class TexLivePlugin(snapcraft.plugins.dump.DumpPlugin):

    def build(self):
        super(dump.DumpPlugin, self).build()

        # Install TexLive with the standard installer
        env = self._build_environment()
        p1 = Popen(['echo', '-n', 'I'], env=env, stdout=PIPE)
        p2 = Popen(['{}/install-tl'.format(self.builddir), '-portable',
                 '-scheme', 'basic'], env=env, stdin=p1.stdout, stdout=PIPE)
        output = p2.communicate()[0]

        base_path = os.path.join(self.installdir, 'texlive', 'bin')
        
        tlmgr_path_x86_64 = os.path.join(base_path, 'x86_64-linux', 'tlmgr')
        tlmgr_path_i386 = os.path.join(base_path, 'i386-linux', 'tlmgr')
        tlmgr_path_armhf = os.path.join(base_path, 'armhf-linux', 'tlmgr')
        tlmgr_path_arm64 = os.path.join(base_path, 'aarch64-linux', 'tlmgr')

        if os.path.exists(tlmgr_path_x86_64):
            self.run([tlmgr_path_x86_64, 'install'] + extras, env=env)
        elif os.path.exists(tlmgr_path_i386):
            self.run([tlmgr_path_i386, 'install'] + extras, env=env)
        elif os.path.exists(tlmgr_path_armhf):
            self.run([tlmgr_path_armhf, 'install'] + extras, env=env)
        elif os.path.exists(tlmgr_path_arm64):
            self.run([tlmgr_path_arm64, 'install'] + extras, env=env)       

    def _build_environment(self):
        env = os.environ.copy()
        env['TEXLIVE_INSTALL_PREFIX'] = os.path.join(self.installdir,
                                                     'texlive')
        return env