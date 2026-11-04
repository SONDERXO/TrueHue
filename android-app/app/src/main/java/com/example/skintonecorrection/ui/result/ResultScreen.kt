package com.example.skintonecorrection.ui.result

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.ui.SharedViewModel

@Composable
fun ResultScreen(sharedViewModel:SharedViewModel,onReSelect:()->Unit){
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    var message by remember{mutableStateOf("")}
    val imageExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("image/png")){destination ->
        val source=state.correctedImageUri
        if(destination!=null && source!=null)sharedViewModel.export(source,destination){message=it}
        else if(destination==null)message="Save cancelled. Your result is unchanged."
    }
    val reportExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){destination ->
        val source=state.reportUri
        if(destination!=null && source!=null)sharedViewModel.export(source,destination){message=it}
        else if(destination==null)message="Save cancelled. Your result is unchanged."
    }
    Scaffold { padding ->
        Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(24.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
            Text("Experimental result",style=MaterialTheme.typography.headlineSmall)
            Text("Older ten-source baseline; failed quality checks. MST is unvalidated. This app is not a finished correction model.",color=MaterialTheme.colorScheme.error)
            listOf("Photo used (256 × 256)" to state.photoUsedUri,"Selected skin" to state.maskUri,"Trial correction" to state.correctedImageUri).forEach { (title,uri) ->
                Text(title,style=MaterialTheme.typography.titleMedium)
                if(uri!=null)AsyncImage(model=uri,contentDescription=title,modifier=Modifier.fillMaxWidth().height(256.dp),contentScale=ContentScale.Fit)
                else Text("Not available")
            }
            Text("Your original is unchanged. Processing and saved reports stay on this phone. Android/Python pixel agreement still needs device verification.")
            if(message.isNotEmpty())Text(message)
            Button(onClick={imageExport.launch("truehue_experimental.png")},enabled=state.correctedImageUri!=null,modifier=Modifier.fillMaxWidth()){Text("Save trial image")}
            OutlinedButton(onClick={reportExport.launch("truehue_report.json")},enabled=state.reportUri!=null,modifier=Modifier.fillMaxWidth()){Text("Save report")}
            OutlinedButton(onClick=onReSelect,modifier=Modifier.fillMaxWidth()){Text("Choose another photo")}
        }
    }
}
