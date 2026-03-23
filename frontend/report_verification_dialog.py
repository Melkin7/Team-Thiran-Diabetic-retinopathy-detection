"""
Report Verification Dialog
Allows user to review generated report before sending to patient
"""

from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os

class ReportVerificationDialog:
    """Dialog for reviewing and confirming report before sending"""
    
    def __init__(self, parent, report_data, pdf_path=None):
        """
        Initialize verification dialog
        
        Args:
            parent: Parent tkinter window
            report_data: Dictionary containing report information
            pdf_path: Path to generated PDF file
        """
        self.report_data = report_data
        self.pdf_path = pdf_path
        self.send_method = StringVar(value="both")  # Options: SMS, WHATSAPP, both
        self.result = None  # Will store user's decision
        
        # Create dialog window
        self.dialog = Toplevel(parent)
        self.dialog.title("Report Verification - Team Thiran DR Detection")
        self.dialog.geometry("900x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configure style
        self.dialog.configure(bg='#f0f4f8')
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        
        # Header
        header_frame = Frame(self.dialog, bg='#1f4788', height=80)
        header_frame.pack(fill=X)
        
        header_label = Label(header_frame, 
                            text="📋 Report Verification",
                            font=('Arial', 14, 'bold'),
                            fg='white',
                            bg='#1f4788')
        header_label.pack(pady=10)
        
        subtitle = Label(header_frame,
                        text="Please review the generated report before sending to patient",
                        font=('Arial', 10),
                        fg='#e0e0e0',
                        bg='#1f4788')
        subtitle.pack()
        
        # Main content frame with scrollbar
        main_frame = Frame(self.dialog, bg='white')
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable text widget
        scrollbar = Scrollbar(main_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        text_widget = Text(main_frame, 
                          yscrollcommand=scrollbar.set,
                          font=('Courier', 9),
                          wrap=WORD,
                          bg='#f8f8f8',
                          relief=SUNKEN,
                          borderwidth=1)
        text_widget.pack(fill=BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Insert report content
        text_widget.insert(END, self._format_report_display())
        text_widget.config(state=DISABLED)  # Make read-only
        
        # Separator
        separator = Frame(self.dialog, height=2, bg='#e0e0e0')
        separator.pack(fill=X, padx=10, pady=5)
        
        # Options frame
        options_frame = Frame(self.dialog, bg='#f0f4f8')
        options_frame.pack(fill=X, padx=10, pady=10)
        
        # Send method selection
        method_label = Label(options_frame,
                            text="How should we send this report to the patient?",
                            font=('Arial', 10, 'bold'),
                            bg='#f0f4f8')
        method_label.pack(anchor=W, pady=(0, 5))
        
        # Radio buttons for sending method
        radio_frame = Frame(options_frame, bg='#f0f4f8')
        radio_frame.pack(anchor=W, padx=20)
        
        sms_radio = Radiobutton(radio_frame,
                               text="📱 SMS Only (for areas without smartphone/internet)",
                               variable=self.send_method,
                               value="sms",
                               font=('Arial', 9),
                               bg='#f0f4f8')
        sms_radio.pack(anchor=W, pady=3)
        
        whatsapp_radio = Radiobutton(radio_frame,
                                    text="💬 WhatsApp Only (sends formatted report with PDF)",
                                    variable=self.send_method,
                                    value="whatsapp",
                                    font=('Arial', 9),
                                    bg='#f0f4f8')
        whatsapp_radio.pack(anchor=W, pady=3)
        
        both_radio = Radiobutton(radio_frame,
                                text="📲 Both SMS & WhatsApp (SMS for notification, WhatsApp with PDF)",
                                variable=self.send_method,
                                value="both",
                                font=('Arial', 9),
                                bg='#f0f4f8')
        both_radio.pack(anchor=W, pady=3)
        
        # Separator
        separator2 = Frame(self.dialog, height=1, bg='#e0e0e0')
        separator2.pack(fill=X, padx=10, pady=5)
        
        # Buttons frame
        button_frame = Frame(self.dialog, bg='#f0f4f8')
        button_frame.pack(fill=X, padx=10, pady=10)
        
        # Verify and Send button
        verify_btn = Button(button_frame,
                           text="✓ Verify & Send",
                           command=self.on_verify,
                           font=('Arial', 10, 'bold'),
                           bg='#4CAF50',
                           fg='white',
                           padx=20,
                           pady=8,
                           relief=RAISED,
                           cursor='hand2')
        verify_btn.pack(side=LEFT, padx=5)
        
        # Edit button
        edit_btn = Button(button_frame,
                         text="✎ Edit Notes",
                         command=self.on_edit,
                         font=('Arial', 10),
                         bg='#2196F3',
                         fg='white',
                         padx=20,
                         pady=8,
                         relief=RAISED,
                         cursor='hand2')
        edit_btn.pack(side=LEFT, padx=5)
        
        # Cancel button
        cancel_btn = Button(button_frame,
                           text="✕ Cancel",
                           command=self.on_cancel,
                           font=('Arial', 10),
                           bg='#f44336',
                           fg='white',
                           padx=20,
                           pady=8,
                           relief=RAISED,
                           cursor='hand2')
        cancel_btn.pack(side=LEFT, padx=5)
    
    def _format_report_display(self):
        """Format report for display in dialog"""
        r = self.report_data
        p = r['patient']
        f = r['findings']
        s = r['screening']
        
        text = f"""{'='*80}
DIABETIC RETINOPATHY SCREENING REPORT
{'='*80}

PATIENT INFORMATION
{'─'*80}
Name:          {p['name']}
Patient ID:    {p['id']}
Age:           {p['age']} years
Gender:        {p['gender']}

SCREENING DETAILS
{'─'*80}
Report ID:     {r['report_id']}
Date/Time:     {r['report_date']}
Physician:     {s['physician']}
Facility:      {s['facility']}
Imaging:       {s['imaging_modality']}

CLINICAL FINDINGS
{'─'*80}
Classification: {f['classification']}
Risk Level:     {f['risk_level']}
Confidence:     {f['confidence']}
Image:          {f['image_analyzed']}

CLINICAL ASSESSMENT
{'─'*80}
{r['clinical_assessment']}

RECOMMENDATIONS
{'─'*80}
{r['recommendations']}

NEXT STEPS
{'─'*80}
"""
        for i, step in enumerate(r['next_steps'], 1):
            text += f"{i}. {step}\n"
        
        text += f"""
{'─'*80}
DISCLAIMER
{'─'*80}
{r['disclaimer']}

PDF Report File: {os.path.basename(self.pdf_path) if self.pdf_path else 'Not Generated'}
{'='*80}"""
        
        return text
    
    def on_verify(self):
        """Handle verify button click"""
        self.result = {
            'verified': True,
            'method': self.send_method.get()
        }
        messagebox.showinfo('Verified', '✓ Report verified! Preparing to send...')
        self.dialog.destroy()
    
    def on_edit(self):
        """Handle edit button click"""
        messagebox.showinfo('Edit', 'Edit functionality coming soon. For now, you can add notes after sending.')
        # In future: Open notes editing dialog
    
    def on_cancel(self):
        """Handle cancel button click"""
        if messagebox.askyesno('Cancel', 'Are you sure you want to cancel sending this report?'):
            self.result = {'verified': False}
            self.dialog.destroy()
    
    def show(self):
        """Show dialog and wait for result"""
        self.dialog.wait_window()
        return self.result


def show_verification_dialog(parent, report_data, pdf_path=None):
    """
    Convenience function to show verification dialog
    
    Args:
        parent: Parent tkinter window
        report_data: Report dictionary
        pdf_path: Path to PDF file
    
    Returns:
        dict: User's verification result
    """
    dialog = ReportVerificationDialog(parent, report_data, pdf_path)
    return dialog.show()
