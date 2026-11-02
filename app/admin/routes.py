from flask import flash, redirect, render_template, url_for

from app import db
from app.admin import bp
from app.admin.forms import CareerForm, CriterionForm, ResetPasswordForm
from app.decorators import admin_required
from app.models import Career, Criterion, RecommendationResult, StudentProfile, User


@bp.route("/")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        n_karier=Career.query.count(),
        n_kriteria=Criterion.query.count(),
        n_profil=StudentProfile.query.count(),
    )


@bp.route("/karier")
@admin_required
def careers():
    daftar = Career.query.order_by(Career.nama).all()
    for c in daftar:
        urut = _urai_skill(c.skills)
        c.top_skills = urut[:5]
        c.n_skill_lain = max(0, len(urut) - 5)
    return render_template("admin/careers.html", careers=daftar)


@bp.route("/karier/<int:cid>")
@admin_required
def career_detail(cid):
    career = Career.query.get_or_404(cid)
    return render_template(
        "admin/career_detail.html", career=career, skills=_urai_skill(career.skills)
    )


def _urai_skill(teks):
    """Urai kolom skills "Nama:skor, ..." jadi list (nama, skor, skor_teks),
    urut dari skor tertinggi. Nama asli dipertahankan untuk tampilan."""
    daftar = []
    for bagian in (teks or "").split(","):
        bagian = bagian.strip()
        if not bagian:
            continue
        if ":" in bagian:
            nama, _, skor_teks = bagian.rpartition(":")
            try:
                skor = float(skor_teks.strip())
            except ValueError:
                skor = 0.0
        else:
            nama, skor_teks, skor = bagian, "", 0.0
        nama = nama.strip()
        if nama:
            daftar.append((nama, skor, skor_teks.strip()))
    daftar.sort(key=lambda x: x[1], reverse=True)
    return daftar


@bp.route("/karier/tambah", methods=["GET", "POST"])
@admin_required
def career_add():
    form = CareerForm()
    if form.validate_on_submit():
        db.session.add(
            Career(
                nama=form.nama.data.strip(),
                deskripsi=form.deskripsi.data.strip(),
                skills=form.skills.data.strip(),
                gaji_min=form.gaji_min.data or 0,
                gaji_max=form.gaji_max.data or 0,
                demand=form.demand.data or 5,
            )
        )
        db.session.commit()
        flash("Data karier ditambahkan.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/career_form.html", form=form, judul="Tambah Karier")


@bp.route("/karier/ubah/<int:cid>", methods=["GET", "POST"])
@admin_required
def career_edit(cid):
    career = Career.query.get_or_404(cid)
    form = CareerForm(obj=career)
    if form.validate_on_submit():
        form.populate_obj(career)
        db.session.commit()
        flash("Data karier diperbarui.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/career_form.html", form=form, judul="Ubah Karier")


@bp.route("/karier/hapus/<int:cid>", methods=["POST"])
@admin_required
def career_delete(cid):
    career = Career.query.get_or_404(cid)
    # hapus hasil rekomendasi terkait agar tidak menjadi data yatim
    RecommendationResult.query.filter_by(career_id=career.id).delete()
    db.session.delete(career)
    db.session.commit()
    flash("Data karier dihapus.", "info")
    return redirect(url_for("admin.careers"))


@bp.route("/kriteria", methods=["GET", "POST"])
@admin_required
def criteria():
    criteria = Criterion.query.order_by(Criterion.kode).all()
    form = CriterionForm()
    if form.validate_on_submit():
        # Kode: isi nomor terkecil 1..4 yang kosong lebih dulu (jalur
        # pemulihan bila kriteria inti pernah rusak), bila C1..C4 sudah
        # lengkap lanjutkan ke C5, C6, ...
        terpakai = {
            int(c.kode[1:])
            for c in Criterion.query.all()
            if c.kode and c.kode.startswith("C") and c.kode[1:].isdigit()
        }
        nomor = next((n for n in (1, 2, 3, 4) if n not in terpakai), None)
        if nomor is None:
            nomor = max(terpakai) + 1 if terpakai else 1
        kode = f"C{nomor}"
        db.session.add(
            Criterion(nama=form.nama.data.strip(), bobot=form.bobot.data, kode=kode)
        )
        db.session.commit()
        flash("Kriteria ditambahkan.", "success")
        return redirect(url_for("admin.criteria"))
    total = round(sum(c.bobot for c in criteria), 4)
    return render_template(
        "admin/criteria.html", criteria=criteria, form=form, total_bobot=total
    )


@bp.route("/kriteria/ubah/<int:cid>", methods=["GET", "POST"])
@admin_required
def criterion_edit(cid):
    criterion = Criterion.query.get_or_404(cid)
    form = CriterionForm(obj=criterion)
    if form.validate_on_submit():
        form.populate_obj(criterion)
        db.session.commit()
        flash("Kriteria diperbarui.", "success")
        return redirect(url_for("admin.criteria"))
    return render_template(
        "admin/criterion_form.html", form=form, criterion=criterion
    )


@bp.route("/kriteria/hapus/<int:cid>", methods=["POST"])
@admin_required
def criterion_delete(cid):
    criterion = Criterion.query.get_or_404(cid)
    if criterion.kode in ("C1", "C2", "C3", "C4"):
        # Kriteria inti tidak boleh dihapus: matriks keputusan SAW
        # dibangun tepat untuk C1..C4, dan bobot dipetakan via kode.
        flash(
            "Kriteria C1 sampai C4 adalah kriteria inti dan tidak dapat "
            "dihapus agar perhitungan SAW tetap sah.",
            "warning",
        )
        return redirect(url_for("admin.criteria"))
    db.session.delete(criterion)
    db.session.commit()
    flash("Kriteria dihapus.", "info")
    return redirect(url_for("admin.criteria"))


@bp.route("/pengguna")
@admin_required
def users():
    daftar = (
        User.query.filter_by(role="mahasiswa").order_by(User.username).all()
    )
    punya_profil = {
        p.user_id for p in StudentProfile.query.with_entities(StudentProfile.user_id)
    }
    for u in daftar:
        u.punya_profil = u.id in punya_profil
    return render_template("admin/users.html", users=daftar)


@bp.route("/pengguna/<int:uid>/reset-sandi", methods=["GET", "POST"])
@admin_required
def user_reset_password(uid):
    # Hanya akun mahasiswa yang boleh direset dari sini; akun admin
    # tidak ditampilkan dan tidak bisa diubah lewat halaman ini.
    user = User.query.filter_by(id=uid, role="mahasiswa").first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.kata_sandi_baru.data)
        # Kata sandi ini hanya sementara: mahasiswa wajib menggantinya
        # sendiri saat login berikutnya (lihat before_request di app).
        user.wajib_ganti_sandi = True
        db.session.commit()
        flash(
            f"Kata sandi sementara akun {user.username} berhasil ditetapkan. "
            "Sampaikan kepada mahasiswanya; ia wajib mengganti kata sandi "
            "saat login berikutnya.",
            "success",
        )
        return redirect(url_for("admin.users"))
    return render_template("admin/user_reset.html", form=form, user=user)
