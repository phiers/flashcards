import random

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import CardCheckForm
from .models import Card


class CardListView(ListView):
    model = Card
    queryset = Card.objects.all().order_by("box", "-date_created")


class CardCreateView(SuccessMessageMixin, CreateView):
    model = Card
    fields = ["question", "answer", "box"]
    success_url = reverse_lazy("card-create")
    success_message = "Question for %(question)s successfully created"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            question = self.object.question.lower()
            )


class CardUpdateView(CardCreateView, UpdateView):
    success_url = reverse_lazy("card-list")
    success_message = "%(question)s card successfully updated"

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(
            cleaned_data,
            question = self.object.question.capitalize()
            )


class BoxView(CardListView):
    # overwrite card_list.html as template_name
    template_name = "cards/box.html"
    form_class = CardCheckForm

    def get_queryset(self):
        return Card.objects.filter(box=self.kwargs["box_num"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_number"] = self.kwargs["box_num"]
        if self.object_list:
            context["check_card"] = random.choice(self.object_list)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            card = get_object_or_404(Card, id=form.cleaned_data["card_id"])
            card.move(form.cleaned_data["solved"])
            if form.cleaned_data["solved"]:
                messages.success(request, "Card moved to next box")

    

        return redirect(request.META.get("HTTP_REFERER"))