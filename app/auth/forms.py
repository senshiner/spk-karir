from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Nama pengguna",
        validators=[DataRequired(message="Nama pengguna wajib diisi.")],
    )
    password = PasswordField(
        "Kata sandi", validators=[DataRequired(message="Kata sandi wajib diisi.")]
    )
    submit = SubmitField("Masuk")


class RegisterForm(FlaskForm):
    nama = StringField(
        "Nama lengkap",
        validators=[
            DataRequired(message="Nama lengkap wajib diisi."),
            Length(max=120, message="Nama maksimal 120 karakter."),
        ],
    )
    username = StringField(
        "Nama pengguna",
        validators=[
            DataRequired(message="Nama pengguna wajib diisi."),
            Length(
                min=3,
                max=80,
                message="Nama pengguna minimal 3 dan maksimal 80 karakter.",
            ),
        ],
    )
    password = PasswordField(
        "Kata sandi",
        validators=[
            DataRequired(message="Kata sandi wajib diisi."),
            Length(min=6, message="Kata sandi minimal 6 karakter."),
        ],
    )
    submit = SubmitField("Daftar")


class ChangePasswordForm(FlaskForm):
    """Ganti kata sandi oleh pengguna yang sedang login."""

    kata_sandi_lama = PasswordField(
        "Kata sandi lama",
        validators=[DataRequired(message="Kata sandi lama wajib diisi.")],
    )
    kata_sandi_baru = PasswordField(
        "Kata sandi baru",
        validators=[
            DataRequired(message="Kata sandi baru wajib diisi."),
            Length(min=6, message="Kata sandi minimal 6 karakter."),
        ],
    )
    konfirmasi = PasswordField(
        "Konfirmasi kata sandi baru",
        validators=[
            DataRequired(message="Konfirmasi kata sandi wajib diisi."),
            EqualTo(
                "kata_sandi_baru",
                message="Konfirmasi tidak sama dengan kata sandi baru.",
            ),
        ],
    )
    submit = SubmitField("Ganti Kata Sandi")
