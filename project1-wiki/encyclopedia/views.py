import random

from django.http import Http404
from django.shortcuts import render, redirect

from . import util
from encyclopedia.forms import CreateEntryForm, EditEntryForm

import markdown2


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    content = util.get_entry(title)

    if content is None:
        raise Http404(f"Entry {title} does not exist.")

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown2.markdown(content)
    })


def search(request):
    pattern = request.GET.get('q', '').upper()
    name_list = util.list_entries()
    suggestions = []

    for name in name_list:
        if pattern == name.upper():
            return redirect('entry', title=name)
        if name.upper().count(pattern) > 0:
            suggestions.append(name)

    return render(request, "encyclopedia/suggestions.html", {
        "suggestions": suggestions
    })


def create(request):
    if request.method == "POST":
        form = CreateEntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect('entry', title=title)
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })

    return render(request, "encyclopedia/create.html", {
        "form": CreateEntryForm()
    })


def edit(request, title):
    if request.method == "POST":
        form = EditEntryForm(request.POST)

        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return redirect('entry', title=title)
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form
            }, title=title)

    content = util.get_entry(title)

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "form": EditEntryForm({"content": content})
    })


def random_page(request):
    name_list = util.list_entries()
    return redirect('entry', title=random.choice(name_list))
