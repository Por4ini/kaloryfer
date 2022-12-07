import base64
import io
import urllib.parse
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import os

# Create your views here.


def index(request):
    if 'charts/index.html' == True:
        os.remove("charts/templates/charts/wykresy.html")
    else:
        with open('charts/templates/charts/wykresy.html', 'w') as f:
            f.write('')
            f.close()
    if request.method == 'POST':
        form = request.POST
        t = form['T']
        Kp = float(form['Kp'])
        u = form['u']
        Tp = 0.1
        t_sim = 3600
        t = [t]
        N = int(t_sim / Tp) + 1
        T_zew = 20.0  # stała temperatura poza pokojem
        K1 = 5
        K2 = 6
        T_oczekiwana = [int(u)]
        # temperatura oczekiwana w pokoju (trzeba pobierać z formularza), najlepiej od razu odrzucać bezsensowne wartości(ujemne, czy powyżej 25 stopni)
        T_grzejnik = [5]
        T_min = 5
        T_max = 60
        T_max_pokoju = 25
        T_pokoj = [5]  # początkowa temperatura w pokoju też mogłaby być wprowadzana
        e = []
        upi = []
        upimin = 0.0
        upimax = 2.0
        Ti = 5  # 5 - 25
        kp = Kp  # 0.01 - 0.025
        q_grzalki = [0.05]
        q_uciekajace_grzalki = [0.0]
        q_grzejnika = [0.05]
        q_uciekajace_grzejnika = [0.0]
        Cw_wody = []
        Cw_powietrza = []
        qmax = 300
        qmin = 0.0

        for n in range(1, N):
            T_oczekiwana.append(T_oczekiwana[-1])
            e.append(T_oczekiwana[-1] - T_pokoj[-1])
            upi.append(min(max(kp * (e[-1] + (Tp / Ti) * sum(e)), upimin), upimax))
            t.append(n * Tp)
            Cw_wody.append(q_grzalki[-1] - q_uciekajace_grzalki[-1])
            Cw_powietrza.append(q_grzejnika[-1] - q_uciekajace_grzejnika[-1])
            q_grzalki.append((qmax - qmin) / (upimax - upimin) * (upi[-1] - upimin) + qmin)
            T_grzejnik.append(
                min(max(
                    1 / Cw_wody[-1] * (q_grzalki[-1] - (K1 * T_grzejnik[-1] + K1 * T_pokoj[-1])) * Tp + T_grzejnik[-1],
                    T_min), T_max))
            q_uciekajace_grzalki.append(K1 * (T_grzejnik[-1] - T_pokoj[-1]))
            q_grzejnika.append(q_grzalki[-1] - Cw_powietrza[-1] + K2 * T_pokoj[-1] - K2 * T_zew)
            T_pokoj.append(
                min(max(1 / Cw_powietrza[-1] * (q_grzejnika[-1] - K2 * T_pokoj[-1]) * Tp + T_pokoj[-1], T_min),
                    T_max_pokoju))
            q_uciekajace_grzejnika.append(K2 * (T_pokoj[-1] - T_zew))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=t,
                y=T_oczekiwana,
                name='oczekiwana temperatura w pokoju',
                line=dict(
                    color="red",
                    width=3
                )
            )
        )
        fig.add_trace(
            go.Scatter(
                x=t,
                y=T_pokoj,
                name='temperatura w pokoju',
                line=dict(
                    color="black",
                    width=3
                )
            )
        )
        fig.add_trace(
            go.Scatter(
                x=t,
                y=T_grzejnik,
                name='temperatura grzejnika',
                line=dict(
                    color="blue",
                    width=3
                )
            )
        )
        fig.update_layout(
            title='Zmiana temperatur',
            xaxis_title='Czas [s]',
            yaxis_title='Temperatura [°C]',
            plot_bgcolor='rgb(204, 230, 255)',
            legend=dict(y=0.5, font_size=16)
        )

        with open('charts/templates/charts/wykresy.html', 'w') as f:
            f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))




    return render(request, 'charts/index.html')

