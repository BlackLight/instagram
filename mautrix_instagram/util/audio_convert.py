# mautrix-instagram - A Matrix-Instagram puppeting bridge.
# Copyright (C) 2021 Tulir Asokan, Sumner Evans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Optional
import mimetypes
import tempfile
import logging
import asyncio
import shutil
import os

log = logging.getLogger("mau.util.audio")


def abswhich(program: Optional[str]) -> Optional[str]:
    if program is None:
        return None
    path = shutil.which(program)
    return os.path.abspath(path) if path else None


async def to_ogg(data: bytes, mime: str) -> Optional[bytes]:
    default_ext = mimetypes.guess_extension(mime)
    with tempfile.TemporaryDirectory(prefix="mxfb_audio_") as tmpdir:
        input_file_name = os.path.join(tmpdir, f"input{default_ext}")
        output_file_name = os.path.join(tmpdir, "output.ogg")
        with open(input_file_name, "wb") as file:
            file.write(data)
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-i",
            input_file_name,
            "-c:a",
            "libvorbis",
            output_file_name,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode == 0:
            with open(output_file_name, "rb") as file:
                return file.read()
        else:
            err_text = (
                stderr.decode("utf-8")
                if stderr is not None
                else f"unknown ({proc.returncode})"
            )
            log.error(f"ffmpeg error: {err_text}")
    return None
