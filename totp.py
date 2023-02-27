from hashlib import sha1

from .lib import pyotp

import keypirinha as kp
import keypirinha_util as kpu


class TOTP(kp.Plugin):
    CATEGORY_TOTP = kp.ItemCategory.USER_BASE + 1

    def _load_config(self):
        uris = self.load_settings().get_multiline('authenticators', 'main')

        self._authenticators.clear()
        for uri in uris:
            self.dbg(f'URI: {uri}')
            try:
                k = sha1(uri.encode()).hexdigest()
                auth = pyotp.parse_uri(uri)
                if not isinstance(auth, pyotp.TOTP):
                    raise TypeError(f'{auth.__class__.__name__} authenticators are not supported')
                self._authenticators[k] = auth
            except Exception as e:
                self.err(f'{e.__class__.__name__}: {e}')

    def on_start(self):
        self._authenticators: dict[str, pyotp.TOTP] = {}
        self._load_config()

    def on_catalog(self):
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=label,
                short_desc='Authenticator',
                target=f'totp_{label}',
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.IGNORE,
            )
            for label in ['Authenticator', 'Auth', 'TOTP']
        ])

    def on_events(self, flags: int):
        if flags & kp.Events.PACKCONFIG:
            self._load_config()

    def on_suggest(self, user_input: str, items_chain: list):
        if not items_chain:
            return

        if not self._authenticators:
            self.set_suggestions(
                    [
                    self.create_error_item(
                        label='No authenticators configured',
                        short_desc='Edit package configuration to add authenticators',
                    ),
                ],
                kp.Match.ANY,
                kp.Sort.NONE,
            )
            return

        self.set_suggestions([
            self.create_item(
                category=self.CATEGORY_TOTP,
                label=auth.name,
                short_desc=auth.now(),
                target=k,
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE,
            )
            for k, auth in self._authenticators.items()
        ])

    def on_execute(self, item, action):
        kpu.set_clipboard(self._authenticators[item.target()].now())
