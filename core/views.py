from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form_inscription import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib import messages
from .models import Genome, Sequence, Annotation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from django.utils.timezone import now
from django.core.paginator import Paginator


from django.http import HttpResponse
#from import_export.formats.base import BaseFormat
from .resources import GenomeResource
from .admin import GenomeImportForm

# Page d'accueil
def page_non_connecte(request):
    return render(request, "core/non_connecte.html")

@login_required
def home(request):
    return render(request,"core/home.html")

# @login_required
# def home(request):
#     if request.user.role == "visiteur":
#         return HttpResponseForbidden("Vous êtes visiteurs : vous n’avez accès à rien.")
#     return render(request, "core/home.html") 


def contacts(request):
    return render(request,"core/contacts.html")

@login_required
def profile(request):
    return render(request, "core/base_profile.html")

@login_required
def profile_informations(request):
    
    validated_count = Annotation.objects.filter(annotation_author=request.user, is_validated=True).count()
    awaiting_count = Annotation.objects.filter(annotation_author=request.user, is_validated=False, sequence__sequence_status="Awaiting validation").count()
    assigned_count = Annotation.objects.filter(annotation_author=request.user, is_validated=False, sequence__sequence_status="Assigned").count()

    return render(request, 'core/profile_informations.html', {
        'validated_count': validated_count,
        'awaiting_count': awaiting_count,
        'assigned_count': assigned_count,
    })

@login_required
def profile_change_PSWD(request):

    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('profile_informations')
    else:  
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'core/profile_change_PSWD.html', {
        'password_form': password_form})

@login_required
def profile_annotations(request):
    status_filter = request.GET.get("filter", "all")
    annotations = Annotation.objects.filter(annotation_author=request.user)

    if status_filter == "validated":
        annotations = annotations.filter(is_validated=True)
    elif status_filter == "awaiting":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Awaiting validation")
    elif status_filter == "assigned":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Assigned")

    annotations_count = annotations.count()

    return render(request, 'core/profile_annotations.html', {'annotations': annotations,'status_filter': status_filter,
        'annotations_count': annotations_count})


def Pageinscription(request):
    return render(request, "core/inscription.html")

def deconnexion(request):
    logout(request)
    return redirect("page_non_connecte")


STATUS_COLORS = {
    "Nothing": "#FFB6C1",  # Rose clair
    "Assigned": "#ADD8E6",  # Bleu clair
    "Awaiting validation": "#FFD700",  # Jaune doré
    "Validated": "#90EE90",  # Vert clair
}

def highlight_sequences(genome_sequence, associated_sequences):
    highlighted = list(genome_sequence)  
    annotations = [] 

    for seq in associated_sequences:
        color = STATUS_COLORS.get(seq.sequence_status, "#D3D3D3")  
        url = f"/visualisation/sequence/{seq.sequence_id}"
        title = f"Gene: {seq.gene_name} ({seq.sequence_start}-{seq.sequence_stop}) - {seq.sequence_status}"

        start, stop = seq.sequence_start, seq.sequence_stop
        annotations.append((start, f'<a href="{url}" title="{title}" style="text-decoration: none; color: inherit;">'
                                   f'<mark style="background-color: {color};">'))
        annotations.append((stop, '</mark></a>'))

    for pos, tag in sorted(annotations, reverse=True):
        highlighted.insert(pos, tag)

    return "".join(highlighted) 


@login_required
def visualisation(request, obj_type, obj_id):
    if obj_type == "genome":
        obj = get_object_or_404(Genome, genome_id=obj_id)
        associated_sequences = obj.sequences.all()
        highlighted_sequence = highlight_sequences(
            obj.genome_sequence, associated_sequences
        )
    elif obj_type == "sequence":
        obj = get_object_or_404(Sequence, sequence_id=obj_id)
        highlighted_sequence = None
    elif obj_type == "annotation":
        obj = get_object_or_404(Annotation, annotation_id=obj_id)
        highlighted_sequence = None
    else:
        return render(request, "core/404.html", {"message": "Type d'objet non reconnu."})

    return render(
        request,
        "core/visualisation.html",
        {
            "obj": obj,
            "obj_type": obj_type,
            "highlighted_sequence": highlighted_sequence,
        },
    )


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "visiteur"
            user.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()

    return render(request, "core/inscription.html", {"form": form})


def connexion(request):
    if request.method == "POST":

        email = request.POST.get("email", "")
        password = request.POST.get("password", "") 


        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect("home")
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")
    return render(request, "core/connexion.html")

def genome_list(request):
    genomes = Genome.objects.all()  # Récupère tous les génomes
    return render(request, "test.html", {"genomes": genomes})


def is_not_visitor(user):
    return user.role != "visiteur"

@login_required
@user_passes_test(is_not_visitor)
def database_view(request):

    user_request = request.GET.get("user_request", "").strip()
    selected_type = request.GET.get("type", "genome") 
    is_annotated = request.GET.get("is_annotated") == "true"
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome")
    sequence_type = request.GET.get("sequence_type")
    Brin = request.GET.get("Brin")

    print(f"""
    User Request: {user_request}
    Filter Types: {', '.join(selected_type) if selected_type else 'None'}
    Is Annotated: {is_annotated}
    Min Length: {min_length if min_length else 'Not specified'}
    Max Length: {max_length if max_length else 'Not specified'}
    Chromosome: {chromosome if chromosome else 'Not specified'}
    Sequence Type: {sequence_type if sequence_type else 'Not specified'}
    Brin: {Brin if Brin else 'Not specified'}
    """)


    genomes = sequences = annotations = None
    
    # Si l'utilisateur n'a pas fait de recherche, afficher le dashboard
    dashboard = not bool(user_request)


    if dashboard:
        
        total_genomes = Genome.objects.count()
        total_species = Genome.objects.values("organism").distinct().count()
        total_sequences = Sequence.objects.count()
        annotated_sequences = Annotation.objects.filter(is_validated=True).values("sequence").distinct().count()
        
        # Calcul de la proportion des séquences annotées
        annotation_ratio = (annotated_sequences / total_sequences * 100) if total_sequences > 0 else 0

        context = {
            "dashboard": True,
            "total_genomes": total_genomes,
            "total_species": total_species,
            "total_sequences": total_sequences,
            "annotation_ratio": annotation_ratio
        }

    else:
        if selected_type == "genome":
            genomes = Genome.objects.filter(
                Q(genome_id__icontains=user_request) | Q(organism__icontains=user_request)
            )
            if is_annotated:
                genomes = genomes.filter(is_annotated=True)
            

        elif selected_type == "sequence":
            sequences = Sequence.objects.filter(
                Q(sequence_id__icontains=user_request) | Q(gene_name__icontains=user_request)
            )
            if min_length:
                sequences = sequences.filter(sequence_length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(sequence_length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(information_support__iexact=chromosome)
            if Brin:
                sequences = sequences.filter(sequence_brin__iexact=Brin)


        combined_results = (
            [{"obj": obj, "type": "Genome"} for obj in genomes] if genomes else []
        ) + (
            [{"obj": obj, "type": "Sequence"} for obj in sequences] if sequences else []
        )

        paginator = Paginator(combined_results, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "dashboard": False,
            "page_obj": page_obj,
            "total_genomes": len(genomes) if genomes else 0,
            "total_sequences": len(sequences) if sequences else 0,
            "selected_type": selected_type,  # Garde la sélection active
        }

    return render(request, "core/database.html", context)

# Vérifier que l'utilisateur est un validateur
def is_validator(user):
    return user.role == "validateur"


@user_passes_test(is_validator)
def annotations_listing(request):
    non_validated_annotations = Annotation.objects.filter(sequence__sequence_status="Awaiting validation")

    return render(request, "core/annotations_non_validates.html", {"annotations": non_validated_annotations})

@user_passes_test(is_validator)
def validate_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, annotation_id=annotation_id)
    sequence = annotation.sequence

    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment", "").strip()

        if action == "validate":
            annotation.is_validated = True
            annotation.validation_date = now()
            sequence.sequence_status = "Validated"
            
        elif action == "reject":
            annotation.is_validated = False
            annotation.rejected_comment = comment
            sequence.sequence_status = "Assigned"

        annotation.save()
        sequence.save()
    
        return redirect("annotations_listing")
    
    return render(request, "core/validation_annotation.html", {"annotation": annotation, "user": request.user})

@user_passes_test(is_validator)
def sequences_non_assigned(request):
    non_assigned_sequence = Sequence.objects.filter(sequence_status="Nothing")
    return render(request, "core/sequences_non_assigned.html", {"sequences": non_assigned_sequence})

@user_passes_test(is_validator)
def attribution_sequence(request, sequence_id):
    sequence_id = get_object_or_404(Sequence, sequence_id = sequence_id)
    annotateurs = CustomUser.objects.filter(role__in=["annotateur", "validateur"])
    
    if request.method == "POST":
        annotateur_id = request.POST.get("annotateur")
        annotateur = get_object_or_404(CustomUser, email = annotateur_id)

        Annotation.objects.create(
            annotation_id=f"ANN_{sequence_id}",
            annotation_text="",
            sequence=sequence_id,
            is_validated=False,
            annotation_author=annotateur
        )

        sequence_id.sequence_status = "Assigned"
        sequence_id.save()

        messages.success(request,  f"La séquence {sequence_id} a été attribuée à {annotateur.email}.")
        return redirect("sequences_non_assigned")

    return render(request, "core/attribution_sequence.html", {"sequence": sequence_id, "annotateurs": annotateurs})

@login_required
def annoter(request, sequence_id):
    sequence = get_object_or_404(Sequence, sequence_id=sequence_id)
    annotation = get_object_or_404(Annotation, sequence=sequence, annotation_author=request.user)

    is_editable = annotation.sequence.sequence_status == "Assigned"

    if request.method == "POST" and is_editable:
        gene_name = request.POST.get('gene_name')
        peptide_product = request.POST.get('peptide_product')
        text = request.POST.get('text')

        sequence.gene_name = gene_name
        sequence.peptide_product = peptide_product
        annotation.annotation_text = text

        if 'send_to_validation' in request.POST:
            sequence.sequence_status = "Awaiting validation"
        
        annotation.save()
        sequence.save()
        
        return redirect("profile_annotations")

    return render(
        request, 
        "core/annoter_sequence.html", 
        {
            "sequence": sequence, 
            "annotation": annotation, 
            "is_editable": is_editable
        }
    )
