"""KNApSAcK: metabolit tanaman. Tidak ada API resmi, jadi halaman pencarian diparse."""
import re
from html import unescape

from dockingku.core.cache import cache
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("sources.knapsack", "KNApSAcK", "KNApSAcK", "parser halaman web", online=True, needs=["httpx"])

SEARCH = "http://www.knapsackfamily.com/knapsack_core/result.php?sname={field}&word={word}"


def search(word: str, field: str = "organism") -> list[dict]:
    """field: organism (nama spesies), metabolite, all. Hasil: C_ID, nama, formula, organisme.

    SMILES tidak tersedia di halaman hasil; lengkapi lewat sources.pubchem.by_name().
    """
    html = cache().get(SEARCH.format(field=field, word=word.replace(" ", "+"))).decode("utf-8", "replace")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        cells = [unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(cells) >= 6 and cells[0].startswith("C0"):
            rows.append({"c_id": cells[0], "cas": cells[1], "name": cells[2],
                         "formula": cells[3], "mw": cells[4], "organism": cells[5]})
    return rows
