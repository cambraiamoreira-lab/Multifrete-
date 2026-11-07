import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Multifrete", page_icon="🚢", layout="centered")

st.title("🚢 Multifrete")
st.caption("Cotador & Precificador de Frete — FCL · LCL · Aéreo")

# ---------------- FUNÇÃO PARA GERAR O TEXTO DA PROPOSTA ----------------
def gerar_proposta_texto(cliente, validade, modal, detalhes, custo_total, margem, preco_venda, lucro):
    hoje = datetime.date.today().strftime('%d/%m/%Y')
    cliente_nome = cliente if cliente else "Não informado"
    validade_proposta = validade if validade else "Não informada"
    
    texto = f"""
==================================================
             MULTIFRETE - PROPOSTA COMERCIAL
==================================================
Data: {hoje}
Cliente: {cliente_nome}
Validade da Proposta: {validade_proposta}

--------------------------------------------------
MODALIDADE: {modal}
--------------------------------------------------
"""
    for linha in detalhes:
        texto += f"- {linha}\n"
        
    texto += f"""
--------------------------------------------------
RESUMO FINANCEIRO (USD)
--------------------------------------------------
Custo Total do Frete: US$ {custo_total:,.2f}
Margem Aplicada: {margem:.1f}%
Lucro Estimado: US$ {lucro:,.2f}

>>> PREÇO DE VENDA: US$ {preco_venda:,.2f} <<<
--------------------------------------------------

Documento gerado automaticamente pelo app Multifrete.
Valores sujeitos a alteração sem aviso prévio.
==================================================
"""
    return texto

# ---------------- SIDEBAR: DADOS GERAIS ----------------
with st.sidebar:
    st.header("⚙️ Configurações da Proposta")
    cliente = st.text_input("Nome do Cliente (para a proposta)")
    validade = st.text_input("Validade da Proposta", placeholder="Ex.: 7 dias")
    margem = st.number_input("Margem de lucro desejada (%)", min_value=0.0, max_value=200.0, value=20.0, step=1.0)
    
    st.markdown("---")
    st.subheader("Custos adicionais (USD)")
    thc_origem = st.number_input("THC Origem", min_value=0.0, value=0.0, step=10.0)
    thc_destino = st.number_input("THC Destino", min_value=0.0, value=0.0, step=10.0)
    baf = st.number_input("BAF / CAF", min_value=0.0, value=0.0, step=10.0)
    seguro = st.number_input("Seguro", min_value=0.0, value=0.0, step=10.0)
    outros = st.number_input("Outros custos", min_value=0.0, value=0.0, step=10.0)

custos_fixos = thc_origem + thc_destino + baf + seguro + outros

# ---------------- ABAS POR MODAL ----------------
aba_fcl, aba_lcl, aba_aereo = st.tabs(["🚛 FCL (Contêiner)", "📦 LCL (Carga Solta)", "✈️ Aéreo"])

# ================= FCL =================
with aba_fcl:
    st.subheader("Dados do FCL")
    col1, col2 = st.columns(2)
    with col1:
        origem_fcl = st.text_input("Origem (porto/aeroporto)", key="origem_fcl", placeholder="Ex.: CNSHA")
        destino_fcl = st.text_input("Destino (porto/aeroporto)", key="destino_fcl", placeholder="Ex.: BRSSZ")
        tipo_container = st.selectbox("Tipo de contêiner", ["20GP", "40GP", "40HC", "45HC"])
        qtd_container = st.number_input("Quantidade de contêineres", min_value=1, value=1, step=1)
    with col2:
        tarifa_fcl = st.number_input("Tarifa base por contêiner (USD)", min_value=0.0, value=0.0, step=100.0)
        st.markdown("**Custo estimado do frete FCL**")
        custo_frete_fcl = qtd_container * tarifa_fcl
        custo_total_fcl = custo_frete_fcl + custos_fixos
        st.metric("Frete base", f"US$ {custo_frete_fcl:,.2f}")
        st.metric("Custo total", f"US$ {custo_total_fcl:,.2f}")

    if custo_total_fcl > 0:
        preco_venda_fcl = custo_total_fcl / (1 - margem / 100) if margem < 100 else custo_total_fcl
        lucro_fcl = preco_venda_fcl - custo_total_fcl
        st.success(f"**Preço de venda sugerido (margem {margem:.1f}%):** US$ {preco_venda_fcl:,.2f}")
        st.info(f"Lucro estimado: US$ {lucro_fcl:,.2f}")
        
        # Botão de Download da Proposta em Texto
        detalhes_fcl = [
            f"Rota: {origem_fcl} -> {destino_fcl}",
            f"Equipamento: {qtd_container}x {tipo_container}",
            f"Tarifa Base: US$ {tarifa_fcl:,.2f} por unidade",
            f"Custos Adicionais Inclusos: US$ {custos_fixos:,.2f}"
        ]
        proposta_fcl = gerar_proposta_texto(cliente, validade, "FCL (Contêiner)", detalhes_fcl, custo_total_fcl, margem, preco_venda_fcl, lucro_fcl)
        st.download_button(label="📄 Baixar Proposta FCL (.txt)", data=proposta_fcl, file_name="Proposta_FCL_Multifrete.txt", mime="text/plain")

# ================= LCL =================
with aba_lcl:
    st.subheader("Dados do LCL")
    col1, col2 = st.columns(2)
    with col1:
        origem_lcl = st.text_input("Origem", key="origem_lcl", placeholder="Ex.: CNSHA")
        destino_lcl = st.text_input("Destino", key="destino_lcl", placeholder="Ex.: BRSSZ")
        peso_lcl = st.number_input("Peso bruto total (kg)", min_value=0.0, value=0.0, step=10.0)
        volume_lcl = st.number_input("Volume total (CBM)", min_value=0.0, value=0.0, step=0.1)
    with col2:
        tarifa_lcl = st.number_input("Tarifa base por W/M (USD)", min_value=0.0, value=0.0, step=10.0)
        st.markdown("**Cálculo W/M**")
        if peso_lcl > 0 or volume_lcl > 0:
            wm = max(peso_lcl / 1000.0, volume_lcl)
            custo_frete_lcl = wm * tarifa_lcl
            custo_total_lcl = custo_frete_lcl + custos_fixos
            st.metric("W/M (peso taxável)", f"{wm:,.3f} W/M")
            st.metric("Frete base", f"US$ {custo_frete_lcl:,.2f}")
            st.metric("Custo total", f"US$ {custo_total_lcl:,.2f}")

            preco_venda_lcl = custo_total_lcl / (1 - margem / 100) if margem < 100 else custo_total_lcl
            lucro_lcl = preco_venda_lcl - custo_total_lcl
            st.success(f"**Preço de venda sugerido:** US$ {preco_venda_lcl:,.2f}")
            st.info(f"Lucro estimado: US$ {lucro_lcl:,.2f}")
            
            # Botão de Download da Proposta em Texto
            detalhes_lcl = [
                f"Rota: {origem_lcl} -> {destino_lcl}",
                f"Peso Bruto: {peso_lcl:,.2f} kg | Volume: {volume_lcl:,.3f} CBM",
                f"Peso Taxável (W/M): {wm:,.3f}",
                f"Tarifa Base: US$ {tarifa_lcl:,.2f} por W/M",
                f"Custos Adicionais Inclusos: US$ {custos_fixos:,.2f}"
            ]
            proposta_lcl = gerar_proposta_texto(cliente, validade, "LCL (Carga Solta)", detalhes_lcl, custo_total_lcl, margem, preco_venda_lcl, lucro_lcl)
            st.download_button(label="📄 Baixar Proposta LCL (.txt)", data=proposta_lcl, file_name="Proposta_LCL_Multifrete.txt", mime="text/plain")
        else:
            wm = 0
            custo_total_lcl = 0
            preco_venda_lcl = 0
            lucro_lcl = 0

# ================= AÉREO =================
with aba_aereo:
    st.subheader("Dados do Aéreo")
    col1, col2 = st.columns(2)
    with col1:
        origem_aereo = st.text_input("Origem", key="origem_aereo", placeholder="Ex.: CNPVG")
        destino_aereo = st.text_input("Destino", key="destino_aereo", placeholder="Ex.: BRGRU")
        peso_bruto = st.number_input("Peso bruto total (kg)", min_value=0.0, value=0.0, step=1.0)
        comprimento = st.number_input("Comprimento por volume (cm)", min_value=0.0, value=0.0, step=1.0)
        largura = st.number_input("Largura por volume (cm)", min_value=0.0, value=0.0, step=1.0)
        altura = st.number_input("Altura por volume (cm)", min_value=0.0, value=0.0, step=1.0)
        qtd_volumes = st.number_input("Quantidade de volumes", min_value=1, value=1, step=1)
    with col2:
        tarifa_aereo = st.number_input("Tarifa base por kg (USD)", min_value=0.0, value=0.0, step=1.0)
        st.markdown("**Peso taxável**")
        if peso_bruto > 0 and comprimento > 0 and largura > 0 and altura > 0:
            volume_total_cm3 = comprimento * largura * altura * qtd_volumes
            peso_volumetrico_total = volume_total_cm3 / 6000.0
            peso_taxavel = max(peso_bruto, peso_volumetrico_total)
            custo_frete_aereo = peso_taxavel * tarifa_aereo
            custo_total_aereo = custo_frete_aereo + custos_fixos

            st.metric("Peso volumétrico total", f"{peso_volumetrico_total:,.2f} kg")
            st.metric("Peso taxável (cobrado)", f"{peso_taxavel:,.2f} kg")
            st.metric("Frete base", f"US$ {custo_frete_aereo:,.2f}")
            st.metric("Custo total", f"US$ {custo_total_aereo:,.2f}")

            preco_venda_aereo = custo_total_aereo / (1 - margem / 100) if margem < 100 else custo_total_aereo
            lucro_aereo = preco_venda_aereo - custo_total_aereo
            st.success(f"**Preço de venda sugerido:** US$ {preco_venda_aereo:,.2f}")
            st.info(f"Lucro estimado: US$ {lucro_aereo:,.2f}")
            
            # Botão de Download da Proposta em Texto
            detalhes_aereo = [
                f"Rota: {origem_aereo} -> {destino_aereo}",
                f"Peso Bruto: {peso_bruto:,.2f} kg | Peso Taxável: {peso_taxavel:,.2f} kg",
                f"Dimensões: {comprimento}x{largura}x{altura} cm ({qtd_volumes} volumes)",
                f"Tarifa Base: US$ {tarifa_aereo:,.2f} por kg",
                f"Custos Adicionais Inclusos: US$ {custos_fixos:,.2f}"
            ]
            proposta_aereo = gerar_proposta_texto(cliente, validade, "Aéreo", detalhes_aereo, custo_total_aereo, margem, preco_venda_aereo, lucro_aereo)
            st.download_button(label="📄 Baixar Proposta Aérea (.txt)", data=proposta_aereo, file_name="Proposta_Aereo_Multifrete.txt", mime="text/plain")
        else:
            peso_taxavel = 0
            custo_total_aereo = 0
            preco_venda_aereo = 0
            lucro_aereo = 0

# ---------------- ANÁLISE COMPARATIVA ----------------
st.markdown("---")
st.header("📊 Análise e Comparação")

resultados = {}
if custo_total_fcl > 0:
    resultados["FCL"] = {"Custo Total": custo_total_fcl, "Preço Venda": preco_venda_fcl, "Lucro": lucro_fcl}
if custo_total_lcl > 0:
    resultados["LCL"] = {"Custo Total": custo_total_lcl, "Preço Venda": preco_venda_lcl, "Lucro": lucro_lcl}
if custo_total_aereo > 0:
    resultados["Aéreo"] = {"Custo Total": custo_total_aereo, "Preço Venda": preco_venda_aereo, "Lucro": lucro_aereo}

if len(resultados) >= 2:
    df = pd.DataFrame(resultados).T
    st.subheader("Comparativo entre modais (USD)")
    st.dataframe(df.style.format("US$ {:,.2f}"))
    st.bar_chart(df[["Custo Total", "Preço Venda"]])

    if "FCL" in resultados and "LCL" in resultados and wm > 0 and tarifa_lcl > 0:
        wm_equilibrio = (qtd_container * tarifa_fcl) / tarifa_lcl if tarifa_lcl > 0 else 0
        if wm_equilibrio > 0:
            st.subheader("⚖️ Ponto de equilíbrio LCL × FCL")
            st.write(
                f"O LCL se torna mais caro que o FCL quando a carga passar de **{wm_equilibrio:,.2f} W/M** "
                f"(considerando {qtd_container} contêiner(es) {tipo_container} a US$ {tarifa_fcl:,.2f}/un. e LCL a US$ {tarifa_lcl:,.2f}/W/M)."
            )
else:
    st.info("Preencha pelo menos **dois modais** para ver a comparação automática.")