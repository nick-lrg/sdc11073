import unittest
from itertools import product
from sdc11073.sdcdevice import localizationservice
from sdc11073.pmtypes import LocalizedText


class TestLocationService(unittest.TestCase):
    def setUp(self):
        self.widthList = ['xs', 's', 'm', 'xl', 'xxl', None] # 'l' is missing
        self.linesList = [1,2,3,4, None]
        self.versionsList = [1,2, None]
        self.langList = ['en-en', 'de-de', 'ru-ru', None]
        self.ref_list = ['a', 'b', 'c', 'd', 'e']
        self.localization_storage = localizationservice.LocalizationStorage()
        for ref in self.ref_list:
            for lang, version, width, lines in product(self.langList, self.versionsList, self.widthList, self.linesList) :
                i_width = localizationservice._tw2i(width) if width else 1
                text = ref * i_width
                if lines in (None, 1):
                    text = ref
                else:
                    text = '\n'.join([ref]*lines)
                self.localization_storage.add(LocalizedText(text, lang=lang, ref=ref, version=version, textWidth=width))


    def test_noFilter(self):
        texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                               requestedVersion=None,
                                                               requestedLangs=None,
                                                               textWidths=None,
                                                               numberOfLines=None)
        self.assertEqual(len(texts), len(self.ref_list) * len(self.langList) *len(self.widthList) * len(self.linesList))  # one version per ref and language
        for t in texts:
            self.assertTrue(t.Version == 2) # highest version only


    def test_refFilter(self):
        handles = ['b', 'c', 'something_different']
        texts = self.localization_storage.filterLocalizedTexts(requestedHandles=handles,
                                                               requestedVersion=None,
                                                               requestedLangs=None,
                                                               textWidths=None,
                                                               numberOfLines=None)
        self.assertEqual(len(texts), 2 * len(self.langList)*len(self.widthList)*len(self.linesList))
        for t in texts:
            self.assertTrue(t.Ref in handles)

    def test_versionFilter(self):
        for version in (1,2):
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=version,
                                                                   requestedLangs=None,
                                                                   textWidths=None,
                                                                   numberOfLines=None)
            self.assertEqual(len(texts), len(self.ref_list) * len(self.langList)*len(self.widthList)*len(self.linesList))  # one version per ref and language
            for t in texts:
                self.assertTrue(t.Version == version)

        texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                               requestedVersion=3,
                                                               requestedLangs=None,
                                                               textWidths=None,
                                                               numberOfLines=None)
        self.assertEqual(len(texts), 0)

    def test_langFilter(self):
        for lang in ('en-en', 'de-de'):
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=[lang],
                                                                   textWidths=None,
                                                                   numberOfLines=None)
            self.assertEqual(len(texts), len(self.ref_list) * len(self.widthList)*len(self.linesList))
            for t in texts:
                self.assertTrue(t.Lang == lang)

        langs = ('en-en', 'de-de')
        texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                               requestedVersion=None,
                                                               requestedLangs=langs,
                                                               textWidths=None,
                                                               numberOfLines=None)
        self.assertEqual(len(texts), len(self.ref_list) * len(self.widthList)*len(self.linesList)*2)


        for t in texts:
            self.assertTrue(t.Lang in langs)

    def test_widthFilter(self):
        for width in ('s', 'xs', 'm', 'xl', 'xxl'):
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=[width],
                                                                   numberOfLines=None)
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList))
            for t in texts:
                self.assertTrue(t.TextWidth == width)
            width = 'l'
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=[width],
                                                                   numberOfLines=None)
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList))
            for t in texts:
                self.assertTrue(t.TextWidth == 'm')

            widths = ['l', 'xl']
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=widths,
                                                                   numberOfLines=None)
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList) *2)
            for t in texts:
                self.assertTrue(t.TextWidth in ('m', 'xl'))

    def test_linesFilter(self):
        for line in (1, 2, 3, 4):
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=None,
                                                                   numberOfLines=[line])
            for t in texts:
                self.assertTrue(t.n_o_l == line)
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList))

            lines = [1,3]
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=None,
                                                                   numberOfLines=lines)
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList) *2)
            for t in texts:
                self.assertTrue(t.n_o_l in lines)

    def test_width_and_linesFilter(self):
        for width, line in product(('s', 'xs', 'm', 'xl', 'xxl'), (1, 2, 3, 4)):
            texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                                   requestedVersion=None,
                                                                   requestedLangs=None,
                                                                   textWidths=[width],
                                                                   numberOfLines=[line])
            for t in texts:
                self.assertLessEqual(t.n_o_l, line)
                self.assertLessEqual(localizationservice._tw2i(t.TextWidth), localizationservice._tw2i(width))
            self.assertEqual(len(texts), len(self.ref_list) *len(self.langList))

        widths = ['xs', 'xl']
        lines = [2,4]
        texts = self.localization_storage.filterLocalizedTexts(requestedHandles=None,
                                                               requestedVersion=None,
                                                               requestedLangs=None,
                                                               textWidths=widths,
                                                               numberOfLines=lines)
        self.assertEqual(len(texts), len(self.ref_list) * len(self.langList)*4)
