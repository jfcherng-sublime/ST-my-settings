from __future__ import annotations

import hashlib
import os
import secrets
from base64 import b64decode, b64encode
from collections.abc import Generator
from dataclasses import dataclass
from textwrap import wrap

import sublime
import sublime_plugin

MY_SECRET_KEY = os.getenv("MY_SECRET_KEY", "")

if not MY_SECRET_KEY:
    print("⚠️ MY_SECRET_KEY environment variable is not set.")


"""
Here is an example PEM block for testing this plugin.

-----BEGIN RAW TEXT-----
Encrypt text using XOR cipher with a key-derived stream.

Args:
    text: The plaintext to encrypt
    key: The encryption key (password)

Returns:
    Base64-encoded encrypted text with salt prefix
-----END RAW TEXT-----
"""


def encrypt(text: str, key: str) -> str:
    """
    Encrypt text using XOR cipher with a key-derived stream.

    Args:
        text: The plaintext to encrypt
        key: The encryption key (password)

    Returns:
        Base64-encoded encrypted text with salt prefix
    """
    # Generate a random salt for key derivation
    salt = secrets.token_bytes(16)
    # Derive encryption key using PBKDF2
    derived_key = hashlib.pbkdf2_hmac("sha256", key.encode(), salt, 100000)
    # Convert text to bytes
    text_bytes = text.encode("utf-8")
    # Encrypt using XOR with derived key (extended to match text length)
    encrypted = bytearray()
    for i, byte in enumerate(text_bytes):
        key_byte = derived_key[i % len(derived_key)]
        encrypted.append(byte ^ key_byte)
    # Combine salt and encrypted data, then encode to base64
    result = salt + bytes(encrypted)
    return b64encode(result).decode("ascii")


def decrypt(encrypted_text: str, key: str) -> str:
    """
    Decrypt text that was encrypted with the encrypt function.

    Args:
        encrypted_text: Base64-encoded encrypted text with salt
        key: The decryption key (must match encryption key)

    Returns:
        The decrypted plaintext

    Raises:
        ValueError: If decryption fails (wrong key or corrupted data)
    """
    try:
        # Decode from base64 (add potential missing padding)
        data = b64decode((encrypted_text + "==").encode("ascii"))
        # Extract salt (first 16 bytes) and encrypted text
        salt = data[:16]
        encrypted_bytes = data[16:]
        # Derive the same key using the extracted salt
        derived_key = hashlib.pbkdf2_hmac("sha256", key.encode(), salt, 100000)
        # Decrypt using XOR
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            key_byte = derived_key[i % len(derived_key)]
            decrypted.append(byte ^ key_byte)
        return bytes(decrypted).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


@dataclass
class PemBlock:
    text: str
    title: str
    wrap_at: int = 80

    def __str__(self) -> str:
        return self.block

    @property
    def header(self) -> str:
        return f"-----BEGIN {self.title}-----"

    @property
    def footer(self) -> str:
        return f"-----END {self.title}-----"

    @property
    def block(self) -> str:
        return f"{self.header}\n{self.text}\n{self.footer}"

    @property
    def block_wrapped(self) -> str:
        return f"{self.header}\n{'\n'.join(wrap(self.text, self.wrap_at))}\n{self.footer}"


def extract_pem_text(text: str, title: str) -> Generator[tuple[PemBlock, tuple[int, int]]]:
    header = f"-----BEGIN {title}-----"
    footer = f"-----END {title}-----"
    start_index = 0
    while True:
        start_index = text.find(header, start_index)
        if start_index == -1:
            break
        end_index = text.find(footer, start_index + len(header))
        if end_index == -1:
            break
        end_index += len(footer)
        pem_block = text[start_index:end_index]
        pem_text = pem_block[len(header) : -len(footer)].strip()
        yield (PemBlock(text=pem_text, title=title), (start_index, end_index))
        start_index = end_index


class InsertRawTextBlockCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        sel = self.view.sel()
        if len(sel) != 1:
            sublime.error_message("You must ONLY have one cursor to insert the block.")
            return
        region = sel[0]

        region_text = self.view.substr(region)
        block_text = PemBlock(text=region_text, title="RAW TEXT").block
        region_new_begin = region.begin() + block_text.index("\n") + 1
        region_new = sublime.Region(region_new_begin, region_new_begin + len(region_text))
        self.view.replace(edit, region, block_text)
        self.view.sel().clear()
        self.view.sel().add(region_new)


class EncryptSelectedCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not MY_SECRET_KEY:
            sublime.error_message("Please set MY_SECRET_KEY environment variable.")
            return

        sel = self.view.sel()
        if sel.has_non_empty_region():
            for region in sel:
                if not region.empty():
                    selected_text = self.view.substr(region)
                    encrypted_text = encrypt(selected_text, MY_SECRET_KEY)
                    self.view.replace(edit, region, encrypted_text)
        else:
            view_text = self.view.substr(sublime.Region(0, self.view.size()))
            for pem, (start_pt, end_pt) in extract_pem_text(view_text, "RAW TEXT"):
                pem.title = "PRIVATE TEXT"
                pem.text = encrypt(pem.text, MY_SECRET_KEY)
                self.view.replace(edit, sublime.Region(start_pt, end_pt), pem.block_wrapped)


class DecryptSelectedCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if not MY_SECRET_KEY:
            sublime.error_message("Please set MY_SECRET_KEY environment variable.")
            return

        sel = self.view.sel()
        if sel.has_non_empty_region():
            for region in sel:
                if not region.empty():
                    selected_text = self.view.substr(region)
                    decrypted_text = decrypt(selected_text, MY_SECRET_KEY)
                    self.view.replace(edit, region, decrypted_text)
        else:
            view_text = self.view.substr(sublime.Region(0, self.view.size()))
            for pem, (start_pt, end_pt) in extract_pem_text(view_text, "PRIVATE TEXT"):
                pem.title = "RAW TEXT"
                pem.text = decrypt(pem.text, MY_SECRET_KEY)
                self.view.replace(edit, sublime.Region(start_pt, end_pt), pem.block)
