'''
This file is a part of Arjuna
Copyright 2015-2020 Rahul Verma

Website: www.RahulVerma.net

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from .gui import *
from arjuna.interact.gui.auto.finder.emd import GuiElementMetaData

class Page(AppContent):

    def __init__(self, *args, source_gui, label=None, gns_dir=None, gns_file_name=None, **kwargs):
        # app = isinstance(source_gui, App) and source_gui or source_gui.app
        super().__init__(automator=source_gui.automator, label=label, gns_dir=gns_dir, gns_file_name=gns_file_name)
        self.app.ui = self
        self._load(*args, **kwargs)

class Section(AppContent):

    def __init__(self, gui, *args, gns_dir=None, root=None, label=None, gns_file_name=None, **kwargs):
        super().__init__(automator=gui.automator, label=label, gns_dir=gns_dir, gns_file_name=gns_file_name)   
        self.__root_meta = self.__determine_root(root)
        self.__root_element = None
        self.__container = self
        self._load(*args, **kwargs)
        self.__parent = gui

    @property
    def root_element(self):
        return self.__root_element

    def __determine_root(self, root_init):
        from arjuna import Locator
        root_label = None
        root_gns = self.gui_def.root_element_name
        if root_init:
            # root in __init__ as a Locator instead of GNS Label
            if isinstance(root_init, Locator):
                root_label = "anonymous"
            else:
                root_label = root_init
        else:
            root_label = root_gns
        from arjuna import log_debug
        log_debug("Setting Root Element for {} Gui. Label: {}. Root in GNS: {}. Root in __init__: {}.".format(
            self.label,
            root_label,
            root_gns,
            root_init
        ))

        if root_label:
            root_label = root_label.lower().strip()
            return root_label, root_init
        else:
            return None

    def load_root_element(self):
        if self.__root_meta:
            label, locator = self.__root_meta
            if self.__root_meta[0] != "anonymous":
                from arjuna import log_debug
                log_debug("Loading Root Element {} for Gui Section: {}".format(label, self.label))
                self.__root_element = getattr(self.gns, label)
            else:
                from arjuna import log_debug
                log_debug("Loading Root Element with Locator {} for Gui Section: {}".format(str(locator), self.label))
                self.__root_element = self.locate(locator)                
            
            self.__container = self.__root_element

    def element(self, *, fargs=None, **kwargs):
        if self.__container is self:
            return super().element(fargs=fargs, **kwargs)
        else:
            return self.__container.element(fargs=fargs, **kwargs)

    def multielement(self, fargs=None, **kwargs):
        if self.__container is self:
            return super().multielement(fargs=fargs, **kwargs)
        else:
            return self.__container.multielement(fargs=fargs, **kwargs)

    def dropdown(self, fargs=None, **kwargs):
        if self.__container is self:
            return super().dropdown(fargs=fargs, **kwargs)
        else:
            return self.__container.dropdown(fargs=fargs, **kwargs)

    def radio_group(self, fargs=None, **kwargs):
        if self.__container is self:
            return super().radio_group(fargs=fargs, **kwargs)
        else:
            return self.__container.radio_group(fargs=fargs, **kwargs)       

    @property
    def parent(self):
        return self.__parent

Widget = Section
Dialog = Section

class App(Gui, metaclass=abc.ABCMeta):

    def __init__(self, *, config=None, ext_config=None, label=None, gns_dir=None, gns_file_name=None):
        gns_dir = gns_dir is not None and gns_dir or ""
        super().__init__(gns_dir=gns_dir, config=config, ext_config=ext_config, label=label)
        self.__ui = None
        self.__automator = None
        self.__gns_file_name = gns_file_name is not None and gns_file_name or "{}.yaml".format(self.label)

    @property
    def automator(self):
        return self.__automator

    def _launchautomator(self):
        # Default Gui automation engine is Selenium
        from arjuna.interact.gui.auto.automator import GuiAutomator
        self.__automator = GuiAutomator(self, self.config, self.ext_config)

    @property
    def ui(self):
        return self.__ui

    @ui.setter
    def ui(self, page):
        self.__ui = page

    def _create_default_ui(self):
        self.__ui = Page(source_gui=self, label=self.label, gns_dir=self.gns_dir, gns_file_name=self.__gns_file_name)

    @abc.abstractmethod
    def launch(self):
        pass

    def prepare_widget(self, widget_object):
        return widget_object


class WebApp(App):

    def __init__(self, *args, base_url=None, blank_slate=False, config=None, ext_config=None, label=None, gns_dir=None, gns_file_name=None, **kwargs):
        '''
            Creates and returns GuiAutomator object for provided config.
            If no configuration is provided reference configuration is used.
            You can also provide GuiDriverExtendedConfig for extended configuration for WebDriver family of libs. 
        '''
        super().__init__(gns_dir=gns_dir, gns_file_name=gns_file_name, config=config, ext_config=ext_config, label=label is None and self.__class__.__name__ or label)
        from arjuna.core.enums import ArjunaOption
        self.__base_url = base_url is not None and base_url or self.config.value(ArjunaOption.APP_URL)
        # self._load(*args, **kwargs)
        self.__args = args
        self.__kwargs = kwargs

    @property
    def base_url(self):
        return self.__base_url

    def launch(self, blank_slate=False):
        self._launchautomator()
        if not blank_slate:
            self.automator.browser.go_to_url(self.base_url)
        self._create_default_ui()
        self._load(*self.__args, **self.__kwargs)

    def quit(self):
        self.automator.quit()

    def __getattr__(self, name):
        return getattr(self.ui, name)