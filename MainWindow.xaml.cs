using HtmlAgilityPack;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;

namespace YoutubeDownloader
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            c_list.AllowDrop = true;
            c_folder.Text = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
        }

        private void OnAddClick(object sender, RoutedEventArgs e)
        {
            if (c_url.Text.Length > 0)
            {
                c_list.Items.Add(c_url.Text);
                c_url.Text = "";
            }
        }

        private void C_list_Drop(object sender, DragEventArgs e)
        {
            string[] formats = e.Data.GetFormats();
            string url = null;
            if (formats.Contains("Text"))
            {
                url = (string)e.Data.GetData("Text");
            }
            else if (formats.Contains("UnicodeText"))
            {
                url = (string)e.Data.GetData("UnicodeText");
            }
            else if (formats.Contains("System.String"))
            {
                url = (string)e.Data.GetData("System.String");
            }

            if (!string.IsNullOrEmpty(url) && url.Contains("http"))
            {
                c_list.Items.Add(url);
            }
        }

        private void C_list_KeyDown(object sender, System.Windows.Input.KeyEventArgs e)
        {
            if (e.Key == System.Windows.Input.Key.Delete)
            {
                List<string> itemsToRemove = new List<string>();
                foreach (string item in c_list.SelectedItems)
                {
                    itemsToRemove.Add(item);
                }

                foreach (string item in itemsToRemove)
                {
                    c_list.Items.Remove(item);
                }

                if (c_list.Items.Count > 0)
                {
                    c_list.SelectedIndex = 0;
                }
            }
        }

        private async void OnDownloadClick(object sender, RoutedEventArgs e)
        {
            HttpClient client = new HttpClient();
            for (int index = 0; index < c_list.Items.Count; index++)
            {
                string item = (string)c_list.Items[index];

                int delimIndex = item.IndexOf(" ::");
                if (delimIndex >= 0)
                {
                    item = item.Substring(0, delimIndex);
                    c_list.Items[index] = item;
                }

                c_list.Items[index] = item + " :: Starting to convert";

                string id_process = null;
                string serverId = null;
                string title = null;
                string keyHash = null;
                string serverUrl = null;
                string dPageId = null;
                try
                {
                    Dictionary<string, string> entries = new Dictionary<string, string>();
                    entries["function"] = "validate";
                    entries["args[dummy]"] = "1";
                    entries["args[urlEntryUser]"] = item;
                    entries["args[fromConvert]"] = "urlconverter";
                    entries["args[requestExt]"] = "mp3";
                    entries["args[nbRetry]"] = "0";
                    entries["args[videoResolution]"] = "-1";
                    entries["args[audioBitrate]"] = "0";
                    entries["args[audioFrequency]"] = "0";
                    entries["args[channel]"] = "stereo";
                    entries["args[volume]"] = "0";
                    entries["args[startFrom]"] = "-1";
                    entries["args[endTo]"] = "-1";
                    entries["args[custom_resx]"] = "-1";
                    entries["args[custom_resy]"] = "-1";
                    entries["args[advSettings]"] = "false";
                    entries["args[aspectRatio]"] = "-1";

                    FormUrlEncodedContent content = new FormUrlEncodedContent(entries);
                    HttpResponseMessage response = await client.PostAsync("https://www2.onlinevideoconverter.com/webservice", content);
                    string responseString = await response.Content.ReadAsStringAsync();
                    dynamic responseObject = JsonConvert.DeserializeObject(responseString);
                    id_process = responseObject.result.id_process;
                    serverId = responseObject.result.serverId;
                    title = responseObject.result.title;
                    keyHash = responseObject.result.keyHash;
                    serverUrl = responseObject.result.serverUrl;
                    dPageId = responseObject.result.dPageId;
                }
                catch (Exception ex)
                {

                }

                if (dPageId == "0")
                {
                    c_list.Items[index] = item + " :: Waiting for conversion";

                    try
                    {
                        Dictionary<string, string> entries = new Dictionary<string, string>();
                        entries["function"] = "processVideo";
                        entries["args[dummy]"] = "1";
                        entries["args[urlEntryUser]"] = item;
                        entries["args[fromConvert]"] = "urlconverter";
                        entries["args[requestExt]"] = "mp3";
                        entries["args[serverId]"] = serverId;
                        entries["args[nbRetry]"] = "0";
                        entries["args[title]"] = title;
                        entries["args[keyHash]"] = keyHash;
                        entries["args[serverUrl]"] = "http://sv43.onlinevideoconverter.com";
                        entries["args[id_process]"] = id_process;
                        entries["args[videoResolution]"] = "-1";
                        entries["args[audioBitrate]"] = "0";
                        entries["args[audioFrequency]"] = "0";
                        entries["args[channel]"] = "stereo";
                        entries["args[volume]"] = "0";
                        entries["args[startFrom]"] = "-1";
                        entries["args[endTo]"] = "-1";
                        entries["args[custom_resx]"] = "-1";
                        entries["args[custom_resy]"] = "-1";
                        entries["args[advSettings]"] = "false";
                        entries["args[aspectRatio]"] = "-1";

                        FormUrlEncodedContent content = new FormUrlEncodedContent(entries);
                        HttpResponseMessage response = await client.PostAsync("https://www2.onlinevideoconverter.com/webservice", content);
                        string responseString = await response.Content.ReadAsStringAsync();
                        dynamic responseObject = JsonConvert.DeserializeObject(responseString);
                        dPageId = responseObject.result.dPageId;
                    }
                    catch (Exception ex)
                    {

                    }
                }

                if (string.IsNullOrEmpty(dPageId) || dPageId == "0")
                {
                    c_list.Items[index] = item + " :: Failed to convert";
                    continue;
                }

                c_list.Items[index] = item + " :: Getting download URL";

                string downloadURL = null;
                try
                {
                    Dictionary<string, string> entries = new Dictionary<string, string>();
                    entries["id"] = dPageId;

                    FormUrlEncodedContent content = new FormUrlEncodedContent(entries);
                    HttpResponseMessage response = await client.PostAsync("https://www.onlinevideoconverter.com/success", content);
                    string responseString = await response.Content.ReadAsStringAsync();

                    HtmlDocument doc = new HtmlDocument();
                    doc.LoadHtml(responseString);
                    HtmlNodeCollection nodes = doc.DocumentNode.SelectNodes("//a[@class='download-button']");
                    if (nodes != null)
                    {
                        foreach (HtmlNode node in nodes)
                        {
                            HtmlAttribute href = node.Attributes["href"];
                            if (href.Value.Contains("http"))
                            {
                                downloadURL = href.Value;
                            }
                        }
                    }
                }
                catch (Exception ex)
                {

                }

                if (string.IsNullOrEmpty(downloadURL))
                {
                    c_list.Items[index] = item + " :: Failed to get download URL";
                    continue;
                }

                c_list.Items[index] = item + " :: Downloading file";
                bool success = false;
                try
                {
                    HttpResponseMessage response = await client.GetAsync(downloadURL);
                    if (response.IsSuccessStatusCode)
                    {
                        string fileName = response.Content.Headers.ContentDisposition.FileName;
                        string regexSearch = new string(Path.GetInvalidFileNameChars()) + new string(Path.GetInvalidPathChars());
                        Regex regex = new Regex(string.Format("[{0}]", Regex.Escape(regexSearch)));
                        fileName = regex.Replace(fileName, "");
                        string filePath = Path.Combine(c_folder.Text, fileName);
                        Stream responseStream = await response.Content.ReadAsStreamAsync();
                        using (FileStream file = File.Create(filePath))
                        {
                            await responseStream.CopyToAsync(file);
                            success = true;
                        }

                        responseStream.Close();
                    }
                }
                catch (Exception ex)
                {

                }

                if (!success)
                {
                    c_list.Items[index] = item + " :: Failed to download file";
                    continue;
                }
                else
                {
                    c_list.Items[index] = item + " :: DONE";
                }
            }
        }
    }
}
