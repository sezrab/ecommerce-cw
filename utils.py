import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def create_pdf_from_2d_list(data, output_filename):
    fig, ax = plt.subplots()
    table = ax.table(cellText=data, loc='center')
    # table.auto_set_font_size(False)
    # table.set_fontsize(12)
    ax.axis('off')
    fig.tight_layout()

    with PdfPages(output_filename) as pdf:
        pdf.savefig(fig)
