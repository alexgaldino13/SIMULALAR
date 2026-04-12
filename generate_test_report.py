import subprocess
import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def run_django_tests():
    """Executa os testes e captura a saída."""
    print("🚀 Executando testes de cenários brasileiros...")
    # Comando para rodar especificamente o arquivo de cenários brasileiros
    cmd = ["python", "manage.py", "test", "simulacao.tests.test_br_scenarios", "--no-input"]
    
    # Capturamos stdout e stderr pois o runner do unittest costuma enviar resultados para o stderr
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + "\n" + result.stderr

def generate_pdf_report(output, filename="Relatorio_Testes_ImobCalc.pdf"):
    """Gera um PDF com a saída dos testes."""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Relatório de Testes Automatizados - ImobCalc")
    
    # Metadados
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Data da Execução: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.drawString(50, height - 85, f"Módulo: simulacao.tests.test_br_scenarios")
    c.line(50, height - 95, width - 50, height - 95)
    
    # Configuração do texto da saída
    text_object = c.beginText(50, height - 120)
    text_object.setFont("Courier", 8)
    text_object.setLeading(10)
    
    lines = output.split('\n')
    for line in lines:
        # Verifica se precisa de nova página
        if text_object.getY() < 50:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Courier", 8)
            text_object.setLeading(10)
        
        # Destaca linhas de sucesso ou falha
        if "OK" in line:
            text_object.setFillColor(colors.green)
        elif "FAIL" in line or "Error" in line:
            text_object.setFillColor(colors.red)
        else:
            text_object.setFillColor(colors.black)
            
        text_object.textLine(line)
        
    c.drawText(text_object)
    c.save()
    print(f"✅ Relatório PDF gerado: {os.path.abspath(filename)}")

if __name__ == "__main__":
    # Garante que o venv está sendo usado se rodado de fora, 
    # mas assumimos execução com venv ativo conforme seu terminal.
    output = run_django_tests()
    
    print("📄 Gerando relatório...")
    generate_pdf_report(output)
    print("✨ Processo concluído.")