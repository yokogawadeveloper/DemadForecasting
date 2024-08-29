export const constant = {
  sidebarDemoLinks: [
    {
      label: "Dashboard",
      link: "/home/dashboard/",
      faIcon: "fa fa-tachometer",
      externalRedirect: false
    },
    {
      label: "File upload",
      faIcon: "fa fa-upload",
      items: [
        {
          label: "Input file",
          icon: "backup",
          link: "home/upload"
        },
        {
          label: "Static file",
          link: "home/staticfilesupload",
          icon: "library_books",
          activeIcon: "favorite"
        }
      ]
    },
    {
      label: "File download",
      icon: "save_alt",
      items: [
        {
          label: "Output file",
          link: "home/download",
          icon: "assignment_returned"
        },
        {
          label: "Static file",
          link: "home/staticfilesdownload",
          icon: "move_to_inbox"
        }
      ]
    },
    {
      label: "Code breakdown",
      link: "/home/codebreakdown/",
      icon: "device_hub",
      externalRedirect: false
    },
  ],
  sidebarConfigurations: {
    paddingAtStart: true,
    interfaceWithRoute: true,
    rtlLayout: false,
    collapseOnSelect: true,
    highlightOnSelect: true,
    classname: "active-amml-item"
  }
};
