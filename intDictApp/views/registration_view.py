from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from intDictApp.forms import SignUpForm
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse


class SignUp(TemplateView):

    template_name = "registration/signup.html"

    def get_context_data(self, **kwargs):
        if "form" not in kwargs:
            # GET request
            form = SignUpForm()
        else:
            # POST request
            form = kwargs['form']

        context = {
            'form': form
        }
        return context

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return HttpResponseRedirect(reverse('categories'))
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context=context)


# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('home')
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})
