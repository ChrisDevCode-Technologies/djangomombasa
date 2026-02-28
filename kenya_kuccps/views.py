import json

from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import (
    County, Institution, Programme, ProgrammeGroup,
    ProgrammeOffering, DegreeCutoff, TvetSection, TvetRequirement,
)

# ── KCSE Constants ──────────────────────────────────────────────────────────

GRADE_POINTS = {
    'A': 12, 'A-': 11, 'B+': 10, 'B': 9, 'B-': 8,
    'C+': 7, 'C': 6, 'C-': 5,
    'D+': 4, 'D': 3, 'D-': 2, 'E': 1,
}

# Ordered high → low for mean-grade-letter lookup
GRADES_DESCENDING = sorted(GRADE_POINTS.items(), key=lambda x: -x[1])

KCSE_SUBJECTS = [
    ('ENG', 'English'), ('KIS', 'Kiswahili'),
    ('MAT A', 'Mathematics'), ('MAT B', 'Mathematics (Alt B)'),
    ('BIO', 'Biology'), ('PHY', 'Physics'), ('CHE', 'Chemistry'),
    ('GEO', 'Geography'), ('HAG', 'History & Government'),
    ('CRE', 'CRE'), ('IRE', 'IRE'), ('HRE', 'HRE'),
    ('HSC', 'Home Science'), ('AGR', 'Agriculture'),
    ('CMP', 'Computer Studies'), ('BST', 'Business Studies'),
    ('FRE', 'French'), ('GER', 'German'), ('ARB', 'Arabic'),
    ('MUC', 'Music'), ('ARD', 'Art & Design'),
    ('WW', 'Woodwork'), ('MW', 'Metalwork'), ('BC', 'Building Construction'),
    ('PM', 'Power Mechanics'), ('ECT', 'Electricity'),
    ('DRD', 'Drawing & Design'), ('AVT', 'Aviation Technology'),
    ('KSL', 'Kenya Sign Language'), ('GSC', 'General Science'),
]

SUBJECT_CODES = {code for code, _ in KCSE_SUBJECTS}


def index(request):
    """KUCCPS project landing page with dataset stats and feature links."""
    stats = {
        'institutions': Institution.objects.count(),
        'counties': County.objects.count(),
        'programmes': Programme.objects.count(),
        'programme_groups': ProgrammeGroup.objects.count(),
        'offerings': ProgrammeOffering.objects.count(),
        'degree_cutoffs': DegreeCutoff.objects.count(),
        'tvet_sections': TvetSection.objects.count(),
        'tvet_requirements': TvetRequirement.objects.count(),
    }
    return render(request, 'kenya_kuccps/index.html', {'stats': stats})


def maps(request):
    """Interactive choropleth maps for county and cluster intelligence."""
    return render(request, 'kenya_kuccps/maps.html')


SUBJECT_NAME_MAP = dict(KCSE_SUBJECTS)

CUTOFF_YEAR_FIELD = {
    '2023': 'cutoff_2023',
    '2024': 'cutoff_2024',
    '2025': 'cutoff_2025',
}


@ensure_csrf_cookie
def eligibility(request):
    """'Where Can I Go?' eligibility checker page."""
    return render(request, 'kenya_kuccps/eligibility.html', {
        'subject_map': SUBJECT_NAME_MAP,
        'grades': list(GRADE_POINTS.keys()),
    })


def _points_to_grade(pts):
    """Convert a numeric mean to the nearest KCSE letter grade."""
    for grade, threshold in GRADES_DESCENDING:
        if pts >= threshold:
            return grade
    return 'E'


def programmes_list_api(request):
    """All programmes for the searchable course dropdown."""
    programmes = (
        Programme.objects
        .select_related('group')
        .order_by('name')
        .values_list('id', 'name', 'group__name')
    )
    data = [
        {'id': str(pid), 'name': name, 'group': group or ''}
        for pid, name, group in programmes
    ]
    return JsonResponse(data, safe=False)


def programme_requirements_api(request, pk):
    """Return parsed subject requirements for a specific programme."""
    try:
        prog = Programme.objects.select_related('group').get(pk=pk)
    except Programme.DoesNotExist:
        return JsonResponse({'error': 'Programme not found'}, status=404)

    cluster_req = prog.cluster_requirements or {}
    subj_req = prog.subject_requirements or {}

    def _enrich(codes):
        """Return list of {code, name} for recognised KCSE subject codes."""
        return [
            {'code': c, 'name': SUBJECT_NAME_MAP.get(c, c)}
            for c in codes if c in SUBJECT_CODES
        ]

    cluster_subjects = []
    for key in sorted(k for k in cluster_req if k.startswith('Cluster Subject')):
        codes = list(dict.fromkeys(c.strip() for c in cluster_req[key].split('/')))
        cluster_subjects.append({
            'slot': key,
            'options': _enrich(codes),
        })

    mandatory_subjects = []
    for key in sorted(k for k in subj_req if k.startswith('Subject')):
        codes = list(dict.fromkeys(c.strip() for c in subj_req[key].split('/')))
        mandatory_subjects.append({
            'slot': key,
            'options': _enrich(codes),
        })

    return JsonResponse({
        'id': str(prog.pk),
        'name': prog.name,
        'group': prog.group.name if prog.group else '',
        'minimum_mean_grade': cluster_req.get('Minimum Mean Grade', 'E'),
        'cluster_subjects': cluster_subjects,
        'mandatory_subjects': mandatory_subjects,
    })


def _build_offering_result(offering, score, cutoff_field, alt_field):
    """Format a single offering result dict."""
    cutoff = float(getattr(offering, cutoff_field))
    score_f = float(score)

    if score_f >= cutoff * 1.10:
        band = 'safe'
    elif score_f >= cutoff * 0.95:
        band = 'competitive'
    elif score_f >= cutoff * 0.80:
        band = 'stretch'
    else:
        return None

    # Trend: compare with alternate year
    trend = 'stable'
    alt_val = getattr(offering, alt_field, None) if alt_field else None
    if alt_val is not None:
        alt_f = float(alt_val)
        if cutoff < alt_f * 0.97:
            trend = 'down'
        elif cutoff > alt_f * 1.03:
            trend = 'up'

    inst = offering.institution
    prog = offering.programme
    return {
        'programme_name': offering.programme_name,
        'programme_group': prog.group.name if prog.group else '',
        'institution': inst.name,
        'county': inst.county.name if inst.county else '',
        'institution_type': (
            inst.institution_type.name if inst.institution_type else ''
        ),
        'institution_category': (
            inst.category.name if inst.category else ''
        ),
        'programme_code': offering.programme_code,
        'cutoff': round(cutoff, 3),
        'student_score': round(score_f, 1),
        'band': band,
        'trend': trend,
    }


def eligibility_api(request):
    """
    Eligibility engine — two modes:
      Quick:    year + mean_grade  → broad search, estimated score
      Detailed: year + mean_grade + programme_id + subjects → precise check
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # ── Common inputs ────────────────────────────────────────────────────
    year = data.get('year', '2024').strip()
    mean_grade_str = data.get('mean_grade', '').strip()
    programme_id = data.get('programme_id', '').strip()
    raw_subjects = data.get('subjects', {})  # dict: code → grade
    county_ids = data.get('counties', [])
    inst_type = data.get('institution_type', '').strip()

    if mean_grade_str not in GRADE_POINTS:
        return JsonResponse({'error': 'Invalid mean grade.'}, status=400)

    mean_points = GRADE_POINTS[mean_grade_str]

    cutoff_field = CUTOFF_YEAR_FIELD.get(year, 'cutoff_2024')

    # KUCCPS advises 2025 applicants to rely on 2023 cut-off points.
    # Fall back to cutoff_2023 when the chosen year has no data yet.
    if not ProgrammeOffering.objects.filter(
        **{f'{cutoff_field}__isnull': False}
    ).exists():
        cutoff_field = 'cutoff_2023'

    alt_field = (
        'cutoff_2023' if cutoff_field == 'cutoff_2024'
        else 'cutoff_2024' if cutoff_field == 'cutoff_2023'
        else 'cutoff_2024'
    )

    # Parse subject grades (for detailed mode)
    student_subjects = {}
    if isinstance(raw_subjects, dict):
        for code, grade in raw_subjects.items():
            code = code.strip()
            grade = grade.strip() if isinstance(grade, str) else ''
            if code in SUBJECT_CODES and grade in GRADE_POINTS:
                student_subjects[code] = GRADE_POINTS[grade]

    # ── Build base queryset ──────────────────────────────────────────────
    qs = (
        ProgrammeOffering.objects
        .filter(**{f'{cutoff_field}__isnull': False})
        .select_related(
            'programme', 'programme__group',
            'institution', 'institution__county',
            'institution__institution_type', 'institution__category',
        )
    )
    if county_ids:
        qs = qs.filter(institution__county_id__in=county_ids)
    if inst_type:
        qs = qs.filter(institution__institution_type__name=inst_type)

    # ── Determine mode ──────────────────────────────────────────────────
    has_subjects = bool(student_subjects)
    mode = 'detailed' if has_subjects else 'quick'

    offerings = list(qs)

    # Cache per-programme: (passes_mean, cluster_score)
    programme_cache = {}  # prog_id → (passes_mean, score)
    results = []

    for offering in offerings:
        prog = offering.programme
        pid = prog.pk

        if pid not in programme_cache:
            cluster_req = prog.cluster_requirements or {}
            min_grade_str = cluster_req.get('Minimum Mean Grade', 'E')
            min_grade_pts = GRADE_POINTS.get(min_grade_str.strip(), 1)
            passes_mean = mean_points >= min_grade_pts

            if not passes_mean:
                programme_cache[pid] = (False, 0)
            elif has_subjects:
                # Calculate actual cluster score for this programme
                cluster_keys = {
                    k: v for k, v in cluster_req.items()
                    if k.startswith('Cluster Subject')
                }
                if cluster_keys:
                    slot_scores = []
                    for slot_key in sorted(cluster_keys.keys()):
                        alternatives = [
                            c.strip()
                            for c in cluster_keys[slot_key].split('/')
                        ]
                        best = max(
                            (student_subjects.get(c, 0) for c in alternatives),
                            default=0,
                        )
                        slot_scores.append(best)
                    score = sum(slot_scores)
                else:
                    # No cluster keys — use best 4 of provided
                    sorted_pts = sorted(
                        student_subjects.values(), reverse=True,
                    )
                    score = sum(sorted_pts[:4])
                programme_cache[pid] = (True, score)
            else:
                # Quick mode — estimate from mean grade
                programme_cache[pid] = (True, mean_points * 4)

        passes, score = programme_cache[pid]
        if not passes:
            continue

        r = _build_offering_result(offering, score, cutoff_field, alt_field)
        if r:
            results.append(r)

    # ── Deduplicate by programme_name + institution ─────────────────────
    # Many offerings differ only by programme_code but have identical
    # cutoffs and the same programme at the same institution. Keep the
    # entry with the highest cutoff (most relevant for the student).
    seen = {}  # (programme_name, institution) → result dict
    for r in results:
        key = (r['programme_name'], r['institution'])
        if key not in seen or r['cutoff'] > seen[key]['cutoff']:
            seen[key] = r
    results = list(seen.values())

    # ── Sort and summarise ───────────────────────────────────────────────
    band_order = {'safe': 0, 'competitive': 1, 'stretch': 2}
    results.sort(key=lambda r: (band_order[r['band']], -r['cutoff']))

    summary = {
        'safe': sum(1 for r in results if r['band'] == 'safe'),
        'competitive': sum(1 for r in results if r['band'] == 'competitive'),
        'stretch': sum(1 for r in results if r['band'] == 'stretch'),
        'total': len(results),
    }

    # Cap results per band so every tab has data to display
    CAP_PER_BAND = 200
    capped = []
    band_counts = {'safe': 0, 'competitive': 0, 'stretch': 0}
    for r in results:
        if band_counts[r['band']] < CAP_PER_BAND:
            capped.append(r)
            band_counts[r['band']] += 1

    return JsonResponse({
        'mode': mode,
        'student': {
            'mean_grade': mean_grade_str,
            'mean_points': mean_points,
            'subject_count': len(student_subjects) if has_subjects else 0,
        },
        'summary': summary,
        'results': capped,
    })


def county_stats_api(request):
    """Per-county institution count, programme count, and institution list."""
    counties = (
        County.objects
        .annotate(
            institution_count=Count('institutions', distinct=True),
            programme_count=Count(
                'institutions__programme_offerings__programme',
                distinct=True,
            ),
        )
        .values('name', 'institution_count', 'programme_count')
    )

    # Build institution lists per county
    institutions_by_county = {}
    for inst in (
        Institution.objects
        .select_related('county', 'category', 'institution_type')
        .filter(county__isnull=False)
    ):
        county_name = inst.county.name
        institutions_by_county.setdefault(county_name, []).append({
            'name': inst.name,
            'code': inst.code,
            'category': str(inst.category) if inst.category else None,
            'type': str(inst.institution_type) if inst.institution_type else None,
        })

    data = {}
    for c in counties:
        data[c['name']] = {
            'institution_count': c['institution_count'],
            'programme_count': c['programme_count'],
            'institutions': institutions_by_county.get(c['name'], []),
        }
    return JsonResponse(data)


def cluster_county_stats_api(request):
    """Per-cluster, per-county offering counts for the cluster map."""
    offerings = (
        ProgrammeOffering.objects
        .filter(
            institution__county__isnull=False,
            programme__group__isnull=False,
        )
        .values(
            group_name=F('programme__group__name'),
            county_name=F('institution__county__name'),
        )
        .annotate(offering_count=Count('id'))
        .order_by('group_name', 'county_name')
    )

    clusters = {}
    for row in offerings:
        gn = row['group_name']
        cn = row['county_name']
        clusters.setdefault(gn, {})[cn] = row['offering_count']

    cluster_list = list(
        ProgrammeGroup.objects.order_by('name').values_list('name', flat=True)
    )

    return JsonResponse({
        'clusters': clusters,
        'cluster_list': cluster_list,
    })
