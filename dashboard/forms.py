from pathlib import Path
from django import forms
from django.core.exceptions import ValidationError

class ExcelUploadForm(forms.Form):
    BEHAVIOR_CHOICES = [
        ('reject', 'Rejeitar valores sem unidade (Padrão)'),
        ('days', 'Interpretar como dias'),
        ('hours', 'Interpretar como horas'),
    ]

    excel_file = forms.FileField(
        label="Planilha de Atestados (.xlsx)",
        help_text="Selecione um arquivo Excel no formato .xlsx. A extensão pode estar escrita em letras maiúsculas ou minúsculas.",
        required=True
    )
    
    default_unit_behavior = forms.ChoiceField(
        choices=BEHAVIOR_CHOICES,
        initial='reject',
        label="Tratamento de valores numéricos sem unidade",
        help_text="Como tratar células que contêm apenas números (ex: '2' ou '8') na coluna de afastamento."
    )

    def clean_excel_file(self):
        uploaded_file = self.cleaned_data.get('excel_file')
        if uploaded_file:
            # Validate extension case-insensitively
            name = uploaded_file.name
            extension = Path(name).suffix.lower()
            if extension != '.xlsx':
                raise ValidationError("Extensão de arquivo inválida. Apenas arquivos .xlsx são suportados.")
            
            # Validate file size (limit to 5MB)
            if uploaded_file.size > 5 * 1024 * 1024:
                raise ValidationError("Tamanho de arquivo excede o limite permitido de 5 MB.")
                
        return uploaded_file
