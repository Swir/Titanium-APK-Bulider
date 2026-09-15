from __future__ import annotations

from .builder_base import AndroidBuilder as _BaseAndroidBuilder
from .validator import ArtifactValidator


class AndroidBuilder(_BaseAndroidBuilder):
    """Android builder with mandatory post-build artifact validation."""

    def build(self, c):
        artifact = super().build(c)
        expect_signed = c["build_mode"] == "Debug" or bool(c["sign_release"])
        report = ArtifactValidator(self.t, self.emit).validate(
            artifact,
            expect_signed=expect_signed,
        )
        self.emit("detail", f"Post-build checks: {', '.join(report.checks)}")
        return artifact
