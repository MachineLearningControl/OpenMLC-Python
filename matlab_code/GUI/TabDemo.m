function TabDemo
%   This function creates a figure with multiple Tabs.
%   The number of tabs can be changed and they are distributed evenly
%   across the top of the figure.  Content is provided for the first 5 tabs
%   to demo the program.  The demo uses the screen size to adjust the size
%   of the figure.  The program uses the ~ character for unused arguments,
%   so if you are not using 2009b, these should be changed to dummy
%   arguments (lines 209 and 233). guidata is set to the TabHandles cell
%   array and is used to pass all arguments and data to the functions.

%%   Set up some varables
%   First clear everything
        clear all
        clc
        
%   Set Number of tabs and tab labels.  Make sure the number of tab labels
%   match the HumberOfTabs setting.
        NumberOfTabs = 6;               % Number of tabs to be generated
        TabLabels = {'Open Image File'; 'Image'; 'Tab3'; 'Tab4'; 'Tab 5'; 'Tab 6'};
        if size(TabLabels,1) ~= NumberOfTabs
            errordlg('Number of tabs and tab labels must be the same','Setup Error');
            return
        end
        
%   Get user screen size
        SC = get(0, 'ScreenSize');
        MaxMonitorX = SC(3);
        MaxMonitorY = SC(4);
        
 %   Set the figure window size values
        MainFigScale = .6;          % Change this value to adjust the figure size
        MaxWindowX = round(MaxMonitorX*MainFigScale);
        MaxWindowY = round(MaxMonitorY*MainFigScale);
        XBorder = (MaxMonitorX-MaxWindowX)/2;
        YBorder = (MaxMonitorY-MaxWindowY)/2; 
        TabOffset = 0;              % This value offsets the tabs inside the figure.
        ButtonHeight = 40;
        PanelWidth = MaxWindowX-2*TabOffset+4;
        PanelHeight = MaxWindowY-ButtonHeight-2*TabOffset;
        ButtonWidth = round((PanelWidth-NumberOfTabs)/NumberOfTabs);
                
 %   Set the color varables.  
        White = [1  1  1];            % White - Selected tab color     
        BGColor = .9*White;           % Light Grey - Background color
            
%%   Create a figure for the tabs
        hTabFig = figure(...
            'Units', 'pixels',...
            'Toolbar', 'none',...
            'Position',[ XBorder, YBorder, MaxWindowX, MaxWindowY ],...
            'NumberTitle', 'off',...
            'Name', 'Tab Demo',...
            'MenuBar', 'none',...
            'Resize', 'off',...
            'DockControls', 'off',...
            'Color', White);
    
%%   Define a cell array for panel and pushbutton handles, pushbuttons labels and other data
    %   rows are for each tab + two additional rows for other data
    %   columns are uipanel handles, selection pushbutton handles, and tab label strings - 3 columns.
            TabHandles = cell(NumberOfTabs,3);
            TabHandles(:,3) = TabLabels(:,1);
    %   Add additional rows for other data
            TabHandles{NumberOfTabs+1,1} = hTabFig;         % Main figure handle
            TabHandles{NumberOfTabs+1,2} = PanelWidth;      % Width of tab panel
            TabHandles{NumberOfTabs+1,3} = PanelHeight;     % Height of tab panel
            TabHandles{NumberOfTabs+2,1} = 0;               % Handle to default tab 2 content(set later)
            TabHandles{NumberOfTabs+2,2} = White;           % Selected tab Color
            TabHandles{NumberOfTabs+2,3} = BGColor;         % Background color
            
%%   Build the Tabs
        for TabNumber = 1:NumberOfTabs
        % create a UIPanel   
            TabHandles{TabNumber,1} = uipanel('Units', 'pixels', ...
                'Visible', 'off', ...
                'Backgroundcolor', White, ...
                'BorderWidth',1, ...
                'Position', [TabOffset TabOffset ...
                PanelWidth PanelHeight]);

        % create a selection pushbutton
            TabHandles{TabNumber,2} = uicontrol('Style', 'pushbutton',...
                'Units', 'pixels', ...
                'BackgroundColor', BGColor, ...
                'Position', [TabOffset+(TabNumber-1)*ButtonWidth PanelHeight+TabOffset...
                    ButtonWidth ButtonHeight], ...          
                'String', TabHandles{TabNumber,3},...
                'HorizontalAlignment', 'center',...
                'FontName', 'arial',...
                'FontWeight', 'bold',...
                'FontSize', 10);

        end

%%   Define the callbacks for the Tab Buttons
%   All callbacks go to the same function with the additional argument being the Tab number
        for CountTabs = 1:NumberOfTabs
            set(TabHandles{CountTabs,2}, 'callback', ...
                {@TabSellectCallback, CountTabs});
        end

%%   Define content for the Open Image File Tab
    %   Open Image Pushbutton
        uicontrol('Parent', TabHandles{1,1}, ...
            'Units', 'pixels', ...
            'Position', [round(PanelWidth/2)-100 2*ButtonHeight 200 ButtonHeight], ...
            'String', 'Open Image File', ...
            'Callback', @OpenImageCallback , ...
            'Style', 'pushbutton',...
            'HorizontalAlignment', 'center',...
            'FontName', 'arial',...
            'FontWeight', 'bold',...
            'FontSize', 12);
 
    %   Build the text for the first tab
        Intro = {'--Tab Demo--';...
            ' ';...
            'Select each tab to see it''s default content.';...
            ' ';...
            'Select below to open an Image in the Image Tab.';...         
            'The Image Tab will become active when the image is opened.';};
        
    %   Display it
        uicontrol('Style', 'text',...
            'Position', [ round(PanelWidth/4) 3*ButtonHeight ...
                round(PanelWidth/2) round(PanelHeight/2) ],...
            'Parent', TabHandles{1,1}, ...
            'string', Intro,...
            'BackgroundColor', White,...
            'HorizontalAlignment', 'center',...
            'FontName', 'arial',...
            'FontWeight', 'bold',...
            'FontSize', 14);
    
%%   Define default content for the Image Tab
    %   Build default text for the Image tab
        Intro = {'Use the Open Image Tab to display an image here'};

    %   Display it - Put the handle in TabHandles so that it can be deleted later 
        TabHandles{NumberOfTabs+2,1} = uicontrol('Style', 'text',...
            'Position', [ round(PanelWidth/4) 3*ButtonHeight ...
                round(PanelWidth/2) round(PanelHeight/2) ],...
            'Parent', TabHandles{2,1}, ...
            'string', Intro,...
            'BackgroundColor', White,...
            'HorizontalAlignment', 'center',...
            'FontName', 'arial',...
            'FontWeight', 'bold',...
            'FontSize', 14);
	   
%%   Define Tab 3 content
    %   Build a table header
        uicontrol('Style', 'text',...
            'Position', [ round((PanelWidth-ButtonWidth)/2) PanelHeight-round(1.5*ButtonHeight) ...
                ButtonWidth ButtonHeight ],...
            'Parent', TabHandles{3,1}, ...
            'string', '  Tab 3 Table ',...
            'BackgroundColor', White,...
            'HorizontalAlignment', 'center',...
            'FontName', 'arial',...
            'FontWeight', 'bold',...
            'FontSize', 12);

    %   Build the data cell array to display
        DisplayData = cell(23,5);
        ColumnNames = {' Column 1 ' ' Column 2 ' ' Column 3 ' ' Column 4 ' ' Column 5 '};
        Width = PanelWidth/5-1;
        ColumnWidths = {Width Width Width Width Width};

    %   Create the table
        uitable('Position',...
            [1 1 PanelWidth PanelHeight-2*ButtonHeight],...
            'Parent', TabHandles{3,1}, ...
            'ColumnName', ColumnNames,...
            'ColumnWidth', ColumnWidths,...
            'RowName', [],...
            'Data', DisplayData);
        
%%   Define Tab 4 content
    %   Create a random RGB image and display it
            Img = rand(PanelHeight,PanelWidth,3);
            ImgOffset = 40;
            haxes4 = axes('Parent', TabHandles{4,1}, ...
                'Units', 'pixels', ...
                'Position', [ImgOffset ImgOffset ...
                    PanelWidth-2*ImgOffset PanelHeight-2*ImgOffset]);
            
            imagesc(Img,'Parent', haxes4);

%%   Define Tab 5 content
    %   Plot a sine function
        PlotOffset = 40;
        haxes2 = axes('Parent', TabHandles{5,1}, ...
            'Units', 'pixels', ...
            'Position', [PlotOffset PlotOffset ...
                PanelWidth-2*PlotOffset PanelHeight-2*PlotOffset]);
        plot(haxes2, 1:200, sin((1:200)./12));

%%   Define Tab 6 content
%   Left blank for now

%%   Save the TabHandles in guidata
        guidata(hTabFig,TabHandles);

%%   Make Tab 1 active
        TabSellectCallback(0,0,1);

end
%%   Callback for Tab Selection
function TabSellectCallback(~,~,SelectedTab)
%   All tab selection pushbuttons are greyed out and uipanels are set to
%   visible off, then the selected panel is made visible and it's selection
%   pushbutton is highlighted.

    %   Set up some varables
        TabHandles = guidata(gcf);
        NumberOfTabs = size(TabHandles,1)-2;
        White = TabHandles{NumberOfTabs+2,2};            % White      
        BGColor = TabHandles{NumberOfTabs+2,3};          % Light Grey
        
    %   Turn all tabs off
        for TabCount = 1:NumberOfTabs
            set(TabHandles{TabCount,1}, 'Visible', 'off');
            set(TabHandles{TabCount,2}, 'BackgroundColor', BGColor);
        end
        
    %   Enable the selected tab
        set(TabHandles{SelectedTab,1}, 'Visible', 'on');        
        set(TabHandles{SelectedTab,2}, 'BackgroundColor', White);

end

%%   Open Image File Callback
    function OpenImageCallback(~,~)
    
    %   Get TabHandles from guidata and set some varables
        TabHandles = guidata(gcf);
        NumberOfTabs = size(TabHandles,1)-2;
        PanelWidth = TabHandles{NumberOfTabs+1,2};
        PanelHeight = TabHandles{NumberOfTabs+1,3};

    %   Two persistent varables are needed
        persistent StartPicDirectory hImageAxes
        
    %   Initilize the StartPicDirectory if first time through
        if isempty(StartPicDirectory)
            StartPicDirectory = cd;
        end
    
    %   Get the file name from the user
        [PicNameWithTag, PicDirectory] = uigetfile({'*.jpg;*.tif;*.png','Image Files'},...
            'Select an image file',StartPicDirectory);

        if PicNameWithTag == 0,
            %   If User canceles then display error message
                errordlg('You should select an Image File');
            return
        end
        
    %   Set the default directory to the currently selected directory
        StartPicDirectory = PicDirectory;

    %   Build path to file
        PicFilePath = strcat(PicDirectory,PicNameWithTag);
            
    %   Load the image
        InitPicRGB = imread(PicFilePath);

    % Get handle of default panel content
        h1 = TabHandles{size(TabHandles,1),1};
        
    %   Delete the previous panel content
        if ishandle(h1)
            delete(h1);             % Delete the default content
        else
            delete(hImageAxes);     % Delete the previous image
        end
        
    %   Set the axes and display the image    
        ImgOffset = 40;
        hImageAxes = axes('Parent', TabHandles{2,1}, ...
            'Units', 'pixels', ...
            'Position', [ImgOffset ImgOffset ...
                PanelWidth-2*ImgOffset PanelHeight-2*ImgOffset]);
            
        image(InitPicRGB,'Parent', hImageAxes);

    %   Make Image Tab active
        TabSellectCallback(0,0,2);
    
    end
       