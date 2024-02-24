import streamlit as st
import pandas as pd
import numpy as np

# Definindo a tabela de valores da espessura de sacrifício
tabela_valores = {
    ("Não Agressivo", "Solos Naturais Inalterados"): {
        5: 0.0,
        25: 0.30,
        50: 0.60
    },
    ("Não Agressivo", "Aterro Compactado(areia, silte, argila etc.)"): {
        5: 0.09,
        25: 0.35,
        50: 0.60
    },
    ("Não Agressivo", "Aterro Não Compactado(areia, silte, argila etc.)"): {
        5: 0.18,
        25: 0.70,
        50: 1.20
    },
    ("Agressivo", "Solos Naturais Poluídos e Regiões Industriais"): {
        5: 0.15,
        25: 0.75,
        50: 1.50
    },
    ("Agressivo", "Solos Naturais (Pântano, Turfa, Solos Orgânicos)"): {
        5: 0.20,
        25: 1.00,
        50: 1.75
    },
    ("Agressivo", "Aterros não compactados ou compactados  (cinzas, escórias etc.)"): {
        5: 0.50,
        25: 2.00,
        50: 3.25
    }
}

def obter_tipos_solo(meio):
    tipos_solo = set()
    for key in tabela_valores.keys():
        if key[0] == meio:
            tipos_solo.add(key[1])
    return list(tipos_solo)

def obter_espessura_sacrificio(meio, tipo_solo, vida_util):
    try:
        espessura = tabela_valores[(meio, tipo_solo)][vida_util]
    except KeyError:
        return None
    return espessura

def calcular_carga_trabalho(Diametro, espessura_sacrificio):
    Area = np.pi * ((Diametro - 2 * espessura_sacrificio) / 1000) ** 2 / 4
    return Area * (500 / 1.15) * 1000

def calcular_qs(referencias, n_spt, d_furo):
    results = []
    for referencia in referencias:
        if referencia == "Ortigão (1997)":
            qs = 50 + 7.5 * n_spt
        elif referencia == "Ortigão et al. (1997)":
            qs = 67 + 60 * np.log(n_spt)  # Using natural logarithm ln
        elif referencia == "Springer (2006)":
            qs =  45.12 * np.log(n_spt) - 14.99
        else:
            qs = None
        results.append(qs)
    Bond_str = [result * np.pi * d_furo * 0.001 for result in results]
    return results, Bond_str

def main():
    # Adicionando o código do Google Tag Manager (gtag.js)
    st.markdown(
        """
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-J47G8X3JRX"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-J47G8X3JRX');
        </script>
        """
        , unsafe_allow_html=True
    )

    st.header('Dimensionamento de Grampos', divider='rainbow')
    #st.title("Dimensionamento de Grampos")

    st.sidebar.title("Opções")
    calculadora_selecionada = st.sidebar.radio("Selecione a opção desejada:", ("Carga de trabalho Ft(Tensile Capacity kN)", "Adesão Solo-Grampo (Bond Stregth kN/m)"))

    if calculadora_selecionada == "Carga de trabalho Ft(Tensile Capacity kN)":
        st.write("Esta aplicação calcula a carga de trabalho com base na espessura de sacrifício.")

        meio = st.radio("Selecione o Meio:", ("Não Agressivo", "Agressivo"))

        tipos_solo = obter_tipos_solo(meio)
        tipo_solo = st.selectbox("Selecione o Tipo de Solo:", tipos_solo)

        if meio:
            vida_util = st.select_slider("Selecione a Vida Útil (em anos):", options=[5, 25, 50])
            Diametro = st.number_input("Digite o valor do diâmetro da bitola do grampo em mm:", min_value=0, value=25)
            if st.button("Calcular"):
                espessura = obter_espessura_sacrificio(meio, tipo_solo, vida_util)
                if espessura is not None:
                    
                    carga_trabalho = calcular_carga_trabalho(Diametro, espessura)
                    st.success(f"A espessura de sacrificio é: {espessura:.1f} mm")
                    st.success(f"A carga de trabalho é: {carga_trabalho:.1f} kN")
                else:
                    st.error("Combinação inválida de seleções.")
    elif calculadora_selecionada == "Adesão Solo-Grampo (Bond Stregth kN/m)":
        st.write("Esta aplicação calcula o valor de qs com base no número de SPT (N(SPT)) e nas referências selecionadas.")
        st.write("também calcula o valor do Bond Strength (kPa/m).")


        n_spt = st.number_input("Digite o valor de N(SPT):", min_value=0)
        d_furo = st.number_input("Digite o valor do diâmetro do furo em mm:", min_value=100)

        referencias = [
            "Ortigão (1997)",
            "Ortigão et al. (1997)",
            "Springer (2006)"
        ]
        referencias_escolhidas = st.multiselect("Escolha as referências:", referencias)

        if st.button("Calcular"):
            if n_spt is not None and referencias_escolhidas:
                resultados_qs, Fs = calcular_qs(referencias_escolhidas, n_spt, d_furo)

                resultados_qs_formatados = [f"{qs:.1f}" if qs is not None else "" for qs in resultados_qs]

                data = {
                    "Referência": referencias_escolhidas,
                    "Valor de qs (kPa)": resultados_qs_formatados,
                    "Valor do Bond Strength (kPa/m)": Fs
                }
                df = pd.DataFrame(data)
                st.table(df)
            else:
                st.error("Por favor, preencha todos os campos.")

if __name__ == "__main__":
    main()
